"""Regressões de perda de dados, chuva ausente, isolamento e publicação."""
import datetime as dt
import json
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from src.core import provenance, storage
from src.core.contracts import merge_observations, observations
from src.eval.cv import folds_por_evento
from src.features.rain import _para_macro, acumulados, api_diaria
from src.live import ingest
from src.models.baselines import _lag_temporal


def observations_fixture():
    idx = pd.date_range('2026-09-01', periods=3, freq='h', tz='UTC')
    return pd.DataFrame({'codigo': [1]*3 + [2]*3, 'ts_utc': list(idx)*2,
                         'nivel_cm': [10., 11., 12., 20., 21., 22.]})


def test_merge_preserva_falha_parcial_e_aplica_nan_explicito():
    hist = observations_fixture()
    new = hist.iloc[[1]].copy()
    new['nivel_cm'] = np.nan
    out = merge_observations(hist, new, 'codigo')
    assert len(out) == 6
    assert out[out.codigo == 2].nivel_cm.tolist() == [20., 21., 22.]
    assert pd.isna(out.iloc[1].nivel_cm)
    pd.testing.assert_frame_equal(merge_observations(hist, pd.DataFrame(), 'codigo'), hist)


def test_contrato_rejeita_duplicatas_fuso_e_infinito():
    hist = observations_fixture()
    with pytest.raises(ValueError, match='duplicada'):
        observations(pd.concat([hist, hist]), 'codigo')
    with pytest.raises(ValueError, match='UTC'):
        observations(hist.assign(ts_utc=hist.ts_utc.dt.tz_localize(None)), 'codigo')
    with pytest.raises(ValueError, match='infinito'):
        observations(hist.assign(nivel_cm=np.inf), 'codigo')


@pytest.mark.parametrize('total', [False, True])
def test_ana_falha_parcial_ou_total_preserva_historico(tmp_path, monkeypatch, total):
    hist = observations_fixture()
    cfg = {'qc': {'tz_fixo_horas': -3},
           'ingest': {'ana_soap': {'base_url': 'mock', 'pausa_s': 0}},
           'stations': {'estacoes_fluviometricas': [{'codigo': 1, 'nome': 'A'},
                                                    {'codigo': 2, 'nome': 'B'}]}}
    monkeypatch.setattr(ingest, 'RAW', tmp_path)
    monkeypatch.setattr(ingest.pd, 'read_parquet', lambda _: hist)
    monkeypatch.setattr(ingest, 'load_config', cfg.__getitem__)
    monkeypatch.setattr(ingest, 'make_client', MagicMock())
    def fetch(client, url, codigo, ini, fim):
        if total or codigo == 2:
            raise RuntimeError('indisponível')
        return pd.DataFrame({'DataHora': ['2026-08-31 21:00']})
    monkeypatch.setattr(ingest, 'fetch_month', fetch)
    monkeypatch.setattr(ingest, 'qc_15min', lambda d, c: d)
    monkeypatch.setattr(ingest, 'para_grade_horaria', lambda d, c:
                        hist[hist.codigo == 1].drop(columns='codigo'))
    out = ingest.ana_recente(dt.date(2026, 9, 28))
    assert len(out) == len(hist)
    assert set(out.codigo) == {1, 2}
    if not total:
        assert list(tmp_path.rglob('*.meta.json'))


def test_ons_catalogo_indisponivel_preserva_historico(monkeypatch):
    hist = observations_fixture().rename(columns={'codigo': 'usina'})
    monkeypatch.setattr(ingest.pd, 'read_parquet', lambda _: hist)
    monkeypatch.setattr(ingest, 'make_client', MagicMock())
    monkeypatch.setattr(ingest, 'get', MagicMock(side_effect=RuntimeError('offline')))
    out = ingest.ons_recente(dt.date(2026, 9, 28))
    pd.testing.assert_frame_equal(out, hist)


@pytest.mark.parametrize('values', [[np.nan, np.nan], [10., np.nan]])
def test_macro_nao_converte_ausencia_em_zero(values):
    h = pd.Timestamp('2026-09-01', tz='UTC')
    df = pd.DataFrame({'ts_utc': [h, h], 'codigo': [1, 2], 'chuva_mm': values})
    areas = pd.DataFrame({'codigo': [1, 2], 'area_incremental_km2': [1., 3.]})
    assert pd.isna(_para_macro(df, {'bacia': [1, 2]}, areas, 'h').iloc[0, 0])
    assert pd.isna(_para_macro(df.iloc[:1], {'bacia': [1, 2]}, areas, 'h').iloc[0, 0])
    df['chuva_mm'] = [4., 8.]
    assert _para_macro(df, {'bacia': [1, 2]}, areas, 'h').iloc[0, 0] == 7.


def test_api_lacuna_invalida_memoria_e_recupera_sem_inventar_chuva():
    idx = pd.date_range('2024-01-01', periods=100, freq='D', tz='UTC')
    d = pd.DataFrame({'bacia': 0.}, index=idx)
    d.iloc[10] = np.nan
    d.iloc[60] = 20.
    api = api_diaria(d, [.9]).iloc[:, 0]
    assert api.iloc[10:54].isna().all()
    assert api.iloc[54] == pytest.approx(0)
    assert api.iloc[60] == pytest.approx(20)
    assert api.iloc[61] == pytest.approx(18)
    d.iloc[80:] = 10000
    pd.testing.assert_series_equal(api.iloc[:80], api_diaria(d, [.9]).iloc[:80, 0])


def test_acumulado_longo_exige_todas_as_horas():
    d = pd.DataFrame({'bacia': np.ones(200)}, index=pd.date_range('2024-01-01', periods=200, freq='h', tz='UTC'))
    d.iloc[100] = np.nan
    out = acumulados(d, [120])
    assert pd.isna(out.iloc[150, 0])


def test_fold_purga_rotulos_e_contexto_de_ambos_os_lados():
    idx = pd.date_range('2024-01-01', periods=1000, freq='h', tz='UTC')
    ds = pd.DataFrame({'janela_id': 'normal', 'tipo': 'normal', 'y_24h': 1.}, index=idx)
    ds.loc[idx[400]:idx[500], ['janela_id', 'tipo']] = ['ev1', 'evento']
    _, tr, te = next(folds_por_evento(ds))
    inicio, fim = te.index.min() - pd.Timedelta(hours=120), te.index.max() + pd.Timedelta(hours=24)
    assert ((tr.index + pd.Timedelta(hours=24) < inicio)
            | (tr.index - pd.Timedelta(hours=120) > fim)).all()
    assert not (tr.index + pd.Timedelta(hours=24)).isin(te.index).any()
    assert len(tr) > 0


def test_lag_temporal_nao_pula_horas_ausentes_ou_janelas():
    idx = pd.date_range('2024-01-01', periods=6, freq='h', tz='UTC').delete(2)
    ds = pd.DataFrame({'nivel': np.arange(5.), 'janela_id': ['a','a','a','b','b']}, index=idx)
    lag = _lag_temporal(ds, 'nivel', 1)
    assert lag.iloc[1] == 0.
    assert pd.isna(lag.iloc[2])
    assert pd.isna(lag.iloc[3])
    assert lag.iloc[4] == 3.


def test_arquivo_anterior_sobrevive_a_falha_de_escrita(tmp_path):
    dest = tmp_path / 'state'
    dest.write_text('valid')
    def fail(tmp):
        tmp.write_text('partial')
        raise OSError('disk failure')
    with pytest.raises(OSError):
        storage.atomic_write(dest, fail)
    assert dest.read_text() == 'valid'
    assert list(tmp_path.iterdir()) == [dest]


def test_lock_rejeita_segundo_escritor(tmp_path):
    with storage.exclusive(tmp_path / 'lock'), pytest.raises(RuntimeError, match='Outra execução'):  # noqa: SIM117
        with storage.exclusive(tmp_path / 'lock'):
            pass


def test_manifesto_invalida_mudanca_mas_permite_append_ao_vivo(tmp_path):
    processed = tmp_path / 'data/processed'
    processed.mkdir(parents=True)
    (tmp_path / 'config').mkdir()
    config = tmp_path / 'config/model.yaml'
    config.write_text('model: 1')
    idx = pd.date_range('2024-01-01', periods=60, freq='h', tz='UTC')
    pd.DataFrame({'ts_utc': idx[:10]}).to_parquet(processed / 'dataset_1.parquet')
    frame = pd.DataFrame({'nivel_mu': np.arange(60.)}, index=idx)
    c = json.loads(json.dumps(provenance.contract(frame, tmp_path)))
    provenance.validate(c, frame, tmp_path)
    future = pd.DataFrame({'nivel_mu': [999.]}, index=[idx[-1] + pd.Timedelta(hours=1)])
    provenance.validate(c, pd.concat([frame, future]), tmp_path)
    changed = frame.copy()
    changed.iloc[1] = 999
    with pytest.raises(RuntimeError, match='mudaram'):
        provenance.validate(c, changed, tmp_path)
    config.write_text('model: 2')
    with pytest.raises(RuntimeError, match='mudaram'):
        provenance.validate(c, frame, tmp_path)
    with pytest.raises(RuntimeError, match='sem contrato'):
        provenance.validate(None, frame, tmp_path)


def test_publicacao_incompleta_nao_aparece_como_emissao(tmp_path, monkeypatch):
    from src.live.archive import registrar
    root = tmp_path
    (root / 'data/processed').mkdir(parents=True)
    t = pd.Timestamp('2024-01-01', tz='UTC')
    prev = pd.DataFrame({'t_ref_utc':[t], 'valido_para_utc':[t], 'status':['estimativa']})
    # Falha ao copiar uv.lock ausente, após escrever previsões no staging.
    with pytest.raises(FileNotFoundError):
        registrar(pd.DataFrame(), prev, pd.DataFrame(), True,
                  root=root, processed=root / 'data/processed', alvos={})
    assert not list((root / 'data/processed/live_runs').glob('emissao_*'))
    assert list((root / 'data/processed/live_runs').glob('.pending_*'))


def test_modelo_salvo_reproduz_previsao_e_invalida_treino(tmp_path):
    from src.models.forecast import fit_cached
    from tests.test_eval import dataset_sintetico
    ds = dataset_sintetico()
    cfg = {}
    first = fit_cached(ds, 86510000, 3, 'linear', cfg, tmp_path)
    loaded = fit_cached(ds, 86510000, 3, 'linear', cfg, tmp_path)
    pd.testing.assert_series_equal(first.predict(ds), loaded.predict(ds))
    assert len(list(tmp_path.glob('*.pkl'))) == 1
    changed = ds.copy()
    changed['y_3h'] += 50
    second = fit_cached(changed, 86510000, 3, 'linear', cfg, tmp_path)
    assert len(list(tmp_path.glob('*.pkl'))) == 2
    assert (second.predict(ds) - first.predict(ds)).dropna().mean() == pytest.approx(50)


def test_early_stopping_tambem_purga_rotulos_e_contexto():
    from src.models.gbm import _split_early_stopping
    idx = pd.date_range('2024-01-01', periods=1000, freq='h', tz='UTC')
    ds = pd.DataFrame({'janela_id':['a']*600 + ['b']*400, 'y_24h':1.}, index=idx)
    train, val = _split_early_stopping(ds, .15)
    assert len(train) > 0
    assert train.index.max() + pd.Timedelta(hours=24) < val.index.min() - pd.Timedelta(hours=120)


def test_cache_detecta_dado_trocado_sem_nova_proveniencia(tmp_path):
    from src.ingest.common import is_cached, write_parquet
    p = tmp_path / 'raw.parquet'
    write_parquet(pd.DataFrame({'a':[1]}), p, url='mock')
    assert is_cached(p)
    # Mesmo tamanho pode esconder conteúdo diferente: o hash precisa detectar.
    data = bytearray(p.read_bytes())
    data[len(data)//2] ^= 1
    p.write_bytes(data)
    assert not is_cached(p)


def test_cenarios_nao_inventam_chuva_passada_e_treino_respeita_referencia(monkeypatch):
    from src.live import cenarios as c
    idx = pd.date_range('2026-01-01', periods=60, freq='h', tz='UTC')
    frame = pd.DataFrame({'nivel_mu': 500., **{f'chuva_{u}_1h': np.nan for u in c.UNIDADES}}, index=idx)
    ds = frame.iloc[:10].assign(janela_id='ev1', tipo='evento', y_6h=550.)
    monkeypatch.setattr(c, 'ALVOS', {86510000: ('Muçum', 'mu')})
    monkeypatch.setattr(c, 'HORIZONTES', (6,))
    monkeypatch.setattr(c, 'montar', lambda f, codigo: ds)
    monkeypatch.setattr(c, 'chuva_postos', lambda f: pd.DataFrame(np.nan, index=idx, columns=list(c.UNIDADES)))
    def fit(train, codigo, h, cols, motor='gbm'):
        assert (train.index + pd.Timedelta(hours=h) < idx[-1]).all()
        return object()
    monkeypatch.setattr(c, 'treinar', fit)
    predictor = MagicMock(return_value=np.array([999.]))
    monkeypatch.setattr(c, 'prever', predictor)
    tab, chuva = c.cenarios(frame, pd.DataFrame(columns=['modelo', 'unidade', 'hora_utc', 'mm']))
    assert tab.previsto_cm.isna().all()
    assert chuva.filter(like='passada_').isna().all(axis=None)
    predictor.assert_not_called()


def test_ana_recupera_meses_da_estacao_atrasada(tmp_path, monkeypatch):
    from src.ingest.ana_soap import CAMPOS
    hist = observations_fixture().iloc[[0, 3]].copy()
    hist.loc[hist.codigo == 2, 'ts_utc'] = pd.Timestamp('2026-07-31 02:00', tz='UTC')
    cfg = {'qc': {'tz_fixo_horas': -3},
           'ingest': {'ana_soap': {'base_url': 'mock', 'pausa_s': 0}},
           'stations': {'estacoes_fluviometricas': [{'codigo': 1, 'nome': 'A'}, {'codigo': 2, 'nome': 'B'}]}}
    monkeypatch.setattr(ingest, 'RAW', tmp_path)
    monkeypatch.setattr(ingest.pd, 'read_parquet', lambda _: hist)
    monkeypatch.setattr(ingest, 'load_config', cfg.__getitem__)
    monkeypatch.setattr(ingest, 'make_client', MagicMock())
    calls = []
    def fetch(client, url, codigo, ini, fim):
        calls.append((codigo, ini.month))
        return pd.DataFrame(columns=CAMPOS)
    monkeypatch.setattr(ingest, 'fetch_month', fetch)
    out = ingest.ana_recente(dt.date(2026, 9, 28))
    # A observação 01/09 00 UTC ainda pertence a agosto no relógio ANA.
    assert calls == [(1, 8), (1, 9), (2, 7), (2, 8), (2, 9)]
    pd.testing.assert_frame_equal(out, hist)


def test_offline_nao_abre_rede(monkeypatch):
    from src.ingest.common import get
    monkeypatch.setenv('FLOOD_OFFLINE', '1')
    client = MagicMock()
    with pytest.raises(RuntimeError, match='offline'):
        get(client, 'https://example.test')
    client.get.assert_not_called()


def test_qc_prefere_download_recente_independente_de_batch_ou_live(tmp_path, monkeypatch):
    from src.ingest.common import meta_path, write_parquet
    from src.qc import ana
    monkeypatch.setattr(ana, 'RAW', tmp_path)
    batch = tmp_path / 'ana_soap/estacao=1/ano=2026/mes=09.parquet'
    live = tmp_path / 'ana_live/1/2026-09.parquet'
    row = pd.DataFrame({'CodEstacao':[1], 'DataHora':['2026-09-01 00:00'], 'Nivel':[10.], 'Vazao':[1.], 'Chuva':[0.]})
    write_parquet(row, live, url='mock')
    write_parquet(row.assign(Nivel=20.), batch, url='mock')
    for p, stamp in [(live,'2026-09-01T00:00:00Z'), (batch,'2026-09-02T00:00:00Z')]:
        meta = json.loads(meta_path(p).read_text())
        meta['downloaded_at_utc'] = stamp
        meta_path(p).write_text(json.dumps(meta))
    assert ana.carregar_estacao(1).Nivel.tolist() == [20.]


def test_offline_tambem_bloqueia_client_direto(monkeypatch):
    from src.ingest.common import make_client
    monkeypatch.setenv('FLOOD_OFFLINE', '1')
    with make_client() as client, pytest.raises(RuntimeError, match='HTTP bloqueado'):
        client.get('https://example.test')


def test_ons_hora_24_gravada_como_2359_vira_hora_cheia():
    import pandas as pd

    from src.core.contracts import observations
    from src.ingest.common import load_config
    from src.qc.ons import processar

    bruto = pd.DataFrame({
        "cod_usina": [97, 97, 97],
        "din_instante": pd.to_datetime(["2026-09-27 23:00", "2026-09-27 23:59", "2026-09-28 01:00"]),
        "val_vazaodefluente": [400.0, 410.0, 420.0],
        "val_vazaoafluente": [400.0, 410.0, 420.0],
    })
    for col in ("val_nivelmontante", "val_niveljusante", "val_vazaoturbinada", "val_vazaovertida"):
        bruto[col] = 1.0
    out = processar(bruto, load_config("qc"))
    observations(out, "usina")
    ts = pd.DatetimeIndex(out.ts_utc)
    assert (ts == ts.floor("h")).all()
    assert pd.Timestamp("2026-09-28 02:00", tz="UTC") in ts  # 23:59 local = fim da hora 23-24


def test_historico_ons_com_2359_e_reparado_sem_duplicar():
    from src.qc.ons import normalizar_hora_24

    hist = pd.DataFrame({
        "usina": ["MONTE CLARO"] * 3,
        "ts_utc": pd.to_datetime(["2026-09-28 01:00", "2026-09-28 01:59", "2026-09-28 03:00"], utc=True),
        "defluente_m3s": [1.0, 2.0, 3.0],
    })
    out = normalizar_hora_24(hist)
    observations(out, "usina")
    assert out.ts_utc.tolist() == list(pd.to_datetime(
        ["2026-09-28 01:00", "2026-09-28 02:00", "2026-09-28 03:00"], utc=True))
