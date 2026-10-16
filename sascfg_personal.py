# sascfg_personal.py

SAS_config_names = ['oda']

oda = {
    'java': 'java',
    # ※ご自身のSAS Studioにログインした際のリージョン（URL）に合わせて変更してください
    #  米国西部（デフォルトで多い）: odaws01-usw2.oda.sas.com
    #  米国東部: odaws01-use1.oda.sas.com
    #  欧州: odaws01-euc1.oda.sas.com
    #  アジア太平洋: odaws01-apse1.oda.sas.com
    'iomhost': 'odaws01-apse1.oda.sas.com',
    'iomport': 8591,
    'authkey': 'oda',
    'encoding': 'utf-8',
}