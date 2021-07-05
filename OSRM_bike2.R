pkgs <- c("osrm", "sp")
sapply(pkgs, require, character.only = T) #load 
crs_OSRM = "+init=EPSG:4326" #WG84
crs = "+init=EPSG:28992"  #Amersfoort / RD New
orig= spTransform(SpatialPoints(coords = as.data.frame(matrix(origin, ncol = 2, nrow = 1)), proj4string = CRS(crs)), CRSobj = crs_OSRM)
dest= spTransform(SpatialPoints(coords = as.data.frame(matrix(destination, ncol = 2, nrow = 1)), proj4string = CRS(crs)), CRSobj = crs_OSRM)
options(osrm.server = "http://127.0.0.1:5001/", osrm.profile = "bike")
route <- osrmRoute(src = as.vector(orig@coords), dst = as.vector(dest@coords), overview = "full", returnclass = "sp")
route = spTransform(route, CRSobj = crs)