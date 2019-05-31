import subprocess

def GetCornerCoordinates(FileName):
  GdalInfo = subprocess.check_output('gdalinfo ' + FileName, shell=True)
  GdalInfo = GdalInfo.decode('utf-8').split('\n') # Creates a line by line list.
  CornerLats, CornerLons = [], []
  GotUL, GotUR, GotLL, GotLR, GotC = False, False, False, False, False
  for line in GdalInfo:
    if line[:10] == 'Upper Left':
        lat, lon = GetLatLon(line)
        CornerLats.append(lat)
        CornerLons.append(lon)
        GotUL = True
    if line[:10] == 'Lower Left':
        lat, lon = GetLatLon(line)
        CornerLats.append(lat)
        CornerLons.append(lon)
        GotLL = True
    if line[:11] == 'Upper Right':
        lat, lon = GetLatLon(line)
        CornerLats.append(lat)
        CornerLons.append(lon)
        GotUR = True
    if line[:11] == 'Lower Right':
        lat, lon = GetLatLon(line)
        CornerLats.append(lat)
        CornerLons.append(lon)
        GotLR = True
    if line[:6] == 'Center':
        lat, lon = GetLatLon(line)
        CornerLats.append(lat)
        CornerLons.append(lon)
        GotC = True
    if GotUL and GotUR and GotLL and GotLR and GotC:
      break
  bounds = [[], []]
  bounds[0].append(min(CornerLats))  
  bounds[1].append(max(CornerLats))  
  bounds[0].append(min(CornerLons))  
  bounds[1].append(max(CornerLons))  
  return bounds 


def GetLatLon(line):
  coords = line.split(') (')[0]
  coords = coords.split('( ')[1]
  LonStr, LatStr = coords.split(', ')
  return float(LatStr), float(LonStr)

