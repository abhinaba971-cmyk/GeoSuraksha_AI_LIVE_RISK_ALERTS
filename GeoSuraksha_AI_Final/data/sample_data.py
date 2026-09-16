STATE_LABELS = [
    {"name":"Sikkim","lat":27.6,"lon":88.5},
    {"name":"Arunachal Pradesh","lat":28.2,"lon":94.7},
    {"name":"Assam","lat":26.3,"lon":92.9},
    {"name":"Nagaland","lat":26.0,"lon":94.5},
    {"name":"Manipur","lat":24.7,"lon":93.9},
    {"name":"Meghalaya","lat":25.5,"lon":91.3},
    {"name":"Mizoram","lat":23.3,"lon":92.8},
    {"name":"Tripura","lat":23.8,"lon":91.5},
]

HOTSPOTS = [
 {"id":"H01","location":"NH-10 Corridor, Sikkim","state":"Sikkim","lat":27.33,"lon":88.62,"rainfall24h":142,"rainfall72h":318,"soilMoisture":91,"slope":42,"elevation":1820,"ndvi":0.31,"historicalDensity":78,"riskScore":87,"confidence":93},
 {"id":"H02","location":"Mangan–Chungthang Road, Sikkim","state":"Sikkim","lat":27.52,"lon":88.53,"rainfall24h":118,"rainfall72h":276,"soilMoisture":84,"slope":39,"elevation":1640,"ndvi":0.35,"historicalDensity":64,"riskScore":74,"confidence":88},
 {"id":"H03","location":"Tawang–Bomdila Highway, Arunachal Pradesh","state":"Arunachal Pradesh","lat":27.59,"lon":92.40,"rainfall24h":96,"rainfall72h":210,"soilMoisture":76,"slope":44,"elevation":2210,"ndvi":0.28,"historicalDensity":71,"riskScore":69,"confidence":85},
 {"id":"H04","location":"Along–Pasighat Road, Arunachal Pradesh","state":"Arunachal Pradesh","lat":28.16,"lon":95.33,"rainfall24h":54,"rainfall72h":132,"soilMoisture":58,"slope":27,"elevation":480,"ndvi":0.52,"historicalDensity":38,"riskScore":41,"confidence":79},
 {"id":"H05","location":"Cherrapunji–Sohra Escarpment, Meghalaya","state":"Meghalaya","lat":25.28,"lon":91.72,"rainfall24h":165,"rainfall72h":402,"soilMoisture":89,"slope":51,"elevation":1290,"ndvi":0.40,"historicalDensity":82,"riskScore":91,"confidence":95},
 {"id":"H06","location":"Shillong–Dawki Road, Meghalaya","state":"Meghalaya","lat":25.32,"lon":91.87,"rainfall24h":88,"rainfall72h":190,"soilMoisture":67,"slope":33,"elevation":990,"ndvi":0.46,"historicalDensity":45,"riskScore":52,"confidence":82},
 {"id":"H07","location":"Haflong Hill Section, Assam","state":"Assam","lat":25.16,"lon":93.02,"rainfall24h":71,"rainfall72h":158,"soilMoisture":62,"slope":29,"elevation":680,"ndvi":0.49,"historicalDensity":40,"riskScore":47,"confidence":80},
 {"id":"H08","location":"Kohima–Dimapur NH-29, Nagaland","state":"Nagaland","lat":25.78,"lon":94.00,"rainfall24h":63,"rainfall72h":141,"soilMoisture":59,"slope":31,"elevation":1150,"ndvi":0.44,"historicalDensity":35,"riskScore":39,"confidence":77},
 {"id":"H09","location":"Imphal–Jiribam Corridor, Manipur","state":"Manipur","lat":24.55,"lon":93.70,"rainfall24h":47,"rainfall72h":105,"soilMoisture":51,"slope":24,"elevation":520,"ndvi":0.55,"historicalDensity":27,"riskScore":29,"confidence":74},
 {"id":"H10","location":"Aizawl–Lunglei Highway, Mizoram","state":"Mizoram","lat":23.44,"lon":92.72,"rainfall24h":102,"rainfall72h":224,"soilMoisture":73,"slope":37,"elevation":1100,"ndvi":0.38,"historicalDensity":58,"riskScore":63,"confidence":84},
 {"id":"H11","location":"Atharamura Range, Tripura","state":"Tripura","lat":23.90,"lon":91.60,"rainfall24h":38,"rainfall72h":84,"soilMoisture":44,"slope":19,"elevation":310,"ndvi":0.58,"historicalDensity":18,"riskScore":19,"confidence":71},
 {"id":"H12","location":"Barapani Catchment, Meghalaya","state":"Meghalaya","lat":25.68,"lon":91.90,"rainfall24h":55,"rainfall72h":119,"soilMoisture":53,"slope":22,"elevation":850,"ndvi":0.50,"historicalDensity":22,"riskScore":24,"confidence":76},
]

INFRASTRUCTURE = [
 {"name":"NH-10 Corridor","type":"Highway","state":"Sikkim","risk":"CRITICAL","priority":94,"nearestHotspot":"H01","action":"Restrict heavy vehicles during critical rainfall; deploy slope sensors."},
 {"name":"Sohra–Dawki Bridge","type":"Bridge","state":"Meghalaya","risk":"CRITICAL","priority":91,"nearestHotspot":"H05","action":"Inspect abutments and drainage; prepare traffic diversion."},
 {"name":"Chungthang Village","type":"Settlement","state":"Sikkim","risk":"HIGH","priority":82,"nearestHotspot":"H02","action":"Community warning and evacuation route readiness."},
 {"name":"Tawang Government School","type":"Public Building","state":"Arunachal Pradesh","risk":"HIGH","priority":76,"nearestHotspot":"H03","action":"Check slope above campus and emergency assembly route."},
 {"name":"Haflong Hill Railway Section","type":"Rail","state":"Assam","risk":"MODERATE","priority":58,"nearestHotspot":"H07","action":"Increase patrol frequency after heavy rainfall."},
 {"name":"Community Health Centre Aizawl","type":"Health","state":"Mizoram","risk":"MODERATE","priority":55,"nearestHotspot":"H10","action":"Protect access road and emergency logistics."},
 {"name":"Dawki Border Road","type":"Road","state":"Meghalaya","risk":"MODERATE","priority":49,"nearestHotspot":"H06","action":"Monitor drainage and rockfall zones."},
 {"name":"Kohima–Dimapur NH-29","type":"Highway","state":"Nagaland","risk":"LOW","priority":33,"nearestHotspot":"H08","action":"Routine slope inspection."},
]
