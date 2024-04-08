import requests
from lxml import etree
import re


# 发送GET请求
baseusl = "https://ieeexplore.ieee.org"
url = "http://ieeexplore.ieee.org/document/80432/"
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
}
cookie = '''AWSALBAPP-1=_remove_; AWSALBAPP-2=_remove_; AWSALBAPP-3=_remove_; osano_consentmanager_uuid=919f79f3-ccdd-4d04-a497-9ccf5a6471ae; osano_consentmanager=l0HfBv-Nr2samoUBHcm8M-HhpQiIMlt5a2uCf8ASadittmXcV_s2JDT7OlhbblDCcySKZRMIKftLT_0rVa8wlDFEG5WDeKHPnsPlR64Xjj4tRZDwIzx97bmEAo3w83LfFQeLjIF_Kk71YiY3g_H6Zlv_7UrZkaFCgocvpJUollk0lS4G1-HBiAm43tSqrKehHAN6p_dykkPUk735G7RS5dhoQnIg7a7t-N5a1w7BY2VgBnrz4oLuQO5hHBlornwVGuQDPumLryrimt8sSe6hdDkDRUqL61obPJ7Pww==; AMCV_8E929CC25A1FB2B30A495C97%40AdobeOrg=T; s_fid=283E2DB12EE341F7-064FCFD1A228FB80; _cc_id=cd86995ab15e3e1fef4345c617c76aef; panoramaId_expiry=1711554650377; panoramaId=2029311532f31ec623474b8a899ba9fb927a0269e974a19d40fabe8b23da4f8d; panoramaIdType=panoDevice; fp=0f2c587061574bf6e58a772b2adc6aba; s_vi=[CS]v1|3301775550F41042-40001C86F73224F7[CE]; s_fid=283E2DB12EE341F7-064FCFD1A228FB80; AMCVS_8E929CC25A1FB2B30A495C97%40AdobeOrg=1; s_cc=true; __gads=ID=b92a03741747a060:T=1711468248:RT=1711505986:S=ALNI_MaI6bcHWahXsfWHiGZriVjYMgbcbg; __gpi=UID=00000d6797461ef2:T=1711468248:RT=1711505986:S=ALNI_MZiJdoDS-4BJ52Ua2hVnsv1w5PRvQ; __eoi=ID=f556bcea0829e965:T=1711468248:RT=1711505986:S=AA-AfjYAe942uUjb1YG1-4kxf9QF; TS01c3e3fe=01f15fc87c9b455a1911ae357f086b6a384d4d37bc357243c4990ba7afd0a60bdf27bb43602603db58ba1b129e47b4eb2d49b54044; ipList=222.70.24.96; TS0118b72b=01f15fc87c9b455a1911ae357f086b6a384d4d37bc357243c4990ba7afd0a60bdf27bb43602603db58ba1b129e47b4eb2d49b54044; JSESSIONID=D07D4CB21B24096EF283DBF5CCF84CE2; ipCheck=222.70.24.96; ERIGHTS=Hb5mCP4WivpMdslSzZ1xxUejZpfSL2j13-18x2dfuunTsP0XHKtMvk9HxxwVuAx3Dx3DfnewzcakuAKWpdPmLitKzgx3Dx3D-Bx2B6Gx2BH9dz1lKd1m1Cx2BWTLQx3Dx3D-PHj1uIXuNf5L22d8rb2R2wx3Dx3D; s_ecid=MCMID%7C73421478083758179220729856139536564794; utag_main=vapi_domain:ieee.org$v_id:018e7b76f9b00009a36cfd87d4c00507d003a0750093c$_sn:2$_se:15$_ss:0$_st:1711507928136$ses_id:1711505985786%3Bexp-session$_pn:6%3Bexp-session; s_sq=ieeexplore.prod%3D%2526c.%2526a.%2526activitymap.%2526page%253DDynamic%252520html%252520doc%252520abstract%2526link%253DAccess%252520Through%252520Fudan%252520University%2526region%253DBODY%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253DDynamic%252520html%252520doc%252520abstract%2526pidt%253D1%2526oid%253DAccess%252520Through%25250AFudan%252520University%2526oidt%253D3%2526ot%253DSUBMIT%26ieeexplore.dev%3D%2526c.%2526a.%2526activitymap.%2526page%253Dhttps%25253A%25252F%25252Fieeexplore.ieee.org%25252FXplore%25252Fguesthome.jsp%25253Fsignout%25253Dsuccess%2526link%253DAccess%252520Through%252520Fudan%252520University%2526region%253DBODY%2526.activitymap%2526.a%2526.c%2526pid%253Dhttps%25253A%25252F%25252Fieeexplore.ieee.org%25252FXplore%25252Fguesthome.jsp%25253Fsignout%25253Dsuccess%2526oid%253DAccess%252520Through%25250AFudan%252520University%2526oidt%253D3%2526ot%253DSUBMIT; AWSALBAPP-0=AAAAAAAAAABpgdQjA3TCbVmjmk5wn5knqnlBfg0yY2YB+A8x4OCCKNECFseqx5KIAO4DnDbT9HB9E74Xoze7vi4U9RYQ/zpx5fu40ze20Sxe2++M4bUy99ThRj5CDl8lgU1CHgHNvfBy//9ACvQhvagzmiGq5u+QSS6gYUg6aerIqketFC8s32tfLWVMDlGRCRMQGabvT5ikTitQmDQdPA==; WLSESSION=1325625866.47873.0000; TS010fc0bf=01f15fc87c1cc6bcef78e171ace95bfcc3ce8965f46a9fe6df93a6e46e5cbd1ae0774f319e56213c6c360371d3f495697ad3891541; TSaf720a17029=0807dc117eab2800f1d6e50fc42e6f16f72113caea316754788c6cd4640e6bbeef17cdc21d18ea0e466c6823d02e1c94; TS8b476361027=0807dc117eab20007b4c7a90908305d073a1ab09a96db577beef514fe179af6c55b0d4c0b0889e4b0841e84337113000398f9ad79f6968ea446a1665ff762f1642f3b3b578a890c06cabfa11fea9deca690c941af42950e406df4fcfb4139b4e'''

session = requests.Session()
response = session.get(url,cookies= {'cookies':cookie},headers=headers)
# https://ieeexplore.ieee.org/iel4/73/2641/00080432.pdf
# 确保请求成功
if response.status_code == 200:
    match = re.search(r'"pdfPath":"(.*?)"', response.text)
    if match:
        pdf_path = match.group(1)
        print(f"提取到的 PDF 路径为: {baseusl + pdf_path}")
    else:
        print("未找到匹配的内容")

pdf_link = session.get(baseusl + pdf_path, cookies={'cookies':cookie}, headers=headers)

print(pdf_link.text)