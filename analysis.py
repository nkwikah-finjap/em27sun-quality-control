"""Audit real reference gas columns and demonstrate XAIR quality screening."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent

def dry_air_fraction(gas_column,o2_column,unit='ppm'):
    gas=np.asarray(gas_column,dtype=float);o2=np.asarray(o2_column,dtype=float)
    if np.any(o2<=0):raise ValueError('O2 column must be positive')
    if unit not in ['ppm','ppb']:raise ValueError('Expected ppm or ppb')
    return gas/o2*0.2095*(1e6 if unit=='ppm' else 1e9)

def sza_correction(sza_degrees,coefficients):
    """PROFFAST v2.4.1 angular correction, normalised at 60 degrees."""
    a,b,c=coefficients
    x=np.radians(np.asarray(sza_degrees))*0.63661977
    xr=0.66666666
    def polynomial(z):
        z4=z**4
        return 1+z4*(a+z4*z4*(b+z4*z4*z4*c))
    return polynomial(x)/polynomial(xr)

def corrected_fraction(frame,gas):
    """Reconstruct this reference output, including documented postprocessing.

    Coefficients are the pinned PROFFASTpylot template defaults, not arbitrary
    fitted factors. The reported XH2O is an input to the water correction.
    These version-specific coefficients must not be assumed for another dataset.
    """
    coefficients={'CO2':(.9970,.0004,.002,0.,-1.15),
                  'CH4':(.9884,.00275,.011,0.,-.72),
                  'CO':(.9997,.0715,.0068,0.,-.3)}
    aicf,a,b,c,h2ocf=coefficients[gas]
    oxygen_fraction=.20942-5.476e-9*(frame.JulianDate-2451545.)
    corrected_o2=frame.O2*.9907*sza_correction(frame.appSZA,[-.0075,-.0072,0.])
    corrected_gas=frame[gas]*aicf*sza_correction(frame.appSZA,[a,b,c])
    return corrected_gas/corrected_o2*oxygen_fraction*1e6*(1+h2ocf*(frame.XH2O*1e-6-.0025))

def screen_xair(frame,daily_threshold=.002,hourly_threshold=.0005):
    f=frame.sort_values('UTC').copy().set_index('UTC')
    if f.index.duplicated().any():raise ValueError('Duplicate times')
    if not np.isfinite(f.XAIR).all():raise ValueError('XAIR must be finite')
    f['daily_reference']=f.groupby(f.index.date).XAIR.transform('median')
    f['daily_pass']=(f.XAIR-f.daily_reference).abs()<=daily_threshold
    f['hourly_reference']=np.nan
    # Stage 2 only uses stage-1 survivors. Centered 60 min window, within each UTC day.
    # It includes the tested point; sensitivity depends on cadence and threshold.
    for _,g in f[f.daily_pass].groupby(lambda t:t.date()):
        f.loc[g.index,'hourly_reference']=g.XAIR.rolling('60min',center=True,min_periods=1).mean()
    f['hourly_pass']=(f.XAIR-f.hourly_reference).abs()<=hourly_threshold
    f['accepted']=f.daily_pass & f.hourly_pass
    return f.reset_index()

def run():
    out=ROOT/'results';out.mkdir(exist_ok=True)
    f=pd.read_csv(ROOT/'data/sodankyla_reference.csv',skipinitialspace=True,parse_dates=['UTC'])
    screened=screen_xair(f)
    for col,gas,unit in [('XCO2','CO2','ppm'),('XCH4','CH4','ppm'),('XCO','CO','ppm')]:
        screened[f'{col}_simple_ratio']=dry_air_fraction(screened[gas],screened.O2,unit)
        screened[f'{col}_reconstructed']=corrected_fraction(screened,gas)
    screened['XCH4_ppb']=screened.XCH4*1000;screened['XCO_ppb']=screened.XCO*1000
    screened.to_csv(out/'screened_observations.csv',index=False)
    errors={c:float(np.max(np.abs(screened[c]-screened[c+'_reconstructed']))) for c in ['XCO2','XCH4','XCO']}
    simple_errors={c:float(np.max(np.abs(screened[c]-screened[c+'_simple_ratio']))) for c in ['XCO2','XCH4','XCO']}
    metrics={'input_rows':len(f),'utc_days':int(f.UTC.dt.date.nunique()),'daily_stage_removed':int((~screened.daily_pass).sum()),
        'hourly_stage_removed':int((screened.daily_pass&~screened.hourly_pass).sum()),'accepted_rows':int(screened.accepted.sum()),
        'max_column_reconstruction_difference_ppm':errors,
        'max_simple_ratio_difference_ppm':simple_errors,
        'reconstruction_note':'Uses documented AICF/angular/time-dependent oxygen corrections and the supplied XH2O. Remaining differences reflect rounded input/output fields; not an independent spectral retrieval.',
        'scope':'Real small reference dataset. Post-retrieval audit; not raw-to-column reprocessing.'}
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2))
    fig,axes=plt.subplots(2,1,figsize=(9,6))
    for day,g in screened.groupby(screened.UTC.dt.date):
        hours=(g.UTC-g.UTC.dt.normalize()).dt.total_seconds()/3600
        axes[0].plot(hours,g.XAIR,'o-',label=str(day))
        axes[1].plot(hours,g.XCO2,'o-',label=str(day))
    axes[0].set(ylabel='XAIR (dimensionless)',title='Real Sodankylä EM27/SUN reference data; 26 observations')
    axes[1].set(ylabel='XCO₂ (ppm)',xlabel='UTC hour')
    for ax in axes:ax.legend();ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'reference_quality.png',dpi=160);plt.close(fig)
    # Controlled anomalies test detection behavior; kept separate from actual measurements.
    injected=f.copy(); injected.loc[3,'XAIR']+=.005
    injected_screen=screen_xair(injected)
    metrics['synthetic_anomaly_experiment_removed_rows']=int((~injected_screen.accepted).sum())
    injected_screen[['UTC','XAIR','accepted']].to_csv(out/'synthetic_anomaly_experiment.csv',index=False)
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2))
    return metrics
if __name__=='__main__':print(json.dumps(run(),indent=2))
