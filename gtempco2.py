import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy import stats
import subprocess as sp
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

def main():
 import requests
 from bs4 import BeautifulSoup
 url = 'https://www.ncei.noaa.gov/data/noaa-global-surface-temperature/v5.1/access/timeseries/'
 response = requests.get(url)
 soup = BeautifulSoup(response.text, 'html.parser')
 links = soup.find_all('a')
 for link in links:
    href = link.get('href')
    if href and 'aravg.mon.land_ocean.90S.90N' in href:
     filenm=href
 print(url+filenm)
 print('enter start_date: e.g. 1960-04')
 print('co2 measurement started from 1958-03')
 start=input('yyyy-mo: ')
 print('enter end_date: e.g. 2023-06')
 end=input('yyyy-mo: ')
 print('start_date=',start,'end_date=',end)
 sp.call(f'wget -nc {url+filenm}', shell=True)
 d=pd.read_csv(filenm,sep='\\s+',header=None)
 d=d.iloc[:, :3]
 d.to_csv('noaa.csv',index=False)
 noaa = pd.read_csv('noaa.csv',comment='#')
 noaa.columns=['year','month','change']

 sp.call('wget -nc ftp://aftp.cmdl.noaa.gov/products/trends/co2/co2_mm_mlo.csv', shell=True)
 co2 = pd.read_csv('co2_mm_mlo.csv',comment='#')
 co2=co2.iloc[:,[0,1,3]]
 #co2.to_csv('co2.csv',index=False) 
 co2['date'] = pd.to_datetime(co2[['year', 'month']].assign(DAY=1)).dt.to_period('M').astype(str)
 noaa['date'] = pd.to_datetime(noaa[['year', 'month']].assign(DAY=1)).dt.to_period('M').astype(str)
 
 start_date = start
 end_date = end
 #start_date = '1958-03'
 #end_date = '1965-12'
 
 mask = (co2['date'] >= start_date) & (co2['date'] <= end_date)
 co2 = co2.loc[mask]
 
 mask = (noaa['date'] >= start_date) & (noaa['date'] <= end_date)
 noaa = noaa.loc[mask]
 
 fig, ax1 = plt.subplots()
 
 ax1.plot(co2['date'].values, co2['average'].values, color='black', linestyle='solid')
 ax1.set_xlabel('Year')
 ax1.set_ylabel('CO2 (ppm)', color='black')
 ax1.tick_params('y', colors='black')
 
 ax2 = ax1.twinx()
 ax2.plot(noaa['date'].values, noaa['change'].values, color='black', linestyle='dotted')
 ax2.set_ylabel('Temperature Anomaly (C)', color='black')
 ax2.tick_params('y', colors='black')
 
 # Add regression lines
 x = np.arange(len(co2))
 slope, intercept, r_value, p_value, std_err = stats.linregress(x, co2['average'])
 ax1.plot(co2['date'].values, intercept + slope * x, 'b', label=f'CO2: y={slope:.3f}x+{intercept:.3f}, R^2={r_value**2:.3f},p-value={p_value:.5f}')
 ax1.legend(loc='upper left')
 
 x = np.arange(len(noaa))
 slope, intercept, r_value, p_value, std_err = stats.linregress(x, noaa['change'])
 ax2.plot(noaa['date'].values, intercept + slope * x, 'r', label=f'T-Anomaly: y={slope:.3f}x+{intercept:.3f},R^2={r_value**2:.3f},p-value={p_value:.5f}')
 ax2.legend(loc='lower right')
 
 ax1.xaxis.set_major_locator(MaxNLocator(7))
 ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
 fig.tight_layout()
 plt.savefig(start+'_'+end+'.png',dpi=300,bbox_inches='tight')
 plt.show()
 
if __name__ == "__main__":
     main()
