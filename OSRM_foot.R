pkgs <- c("osrm", "sf")
sapply(pkgs, require, character.only = T) #load 
crs = "+init=EPSG:28992"  #Amersfoort / RD New
options(osrm.server = "http://127.0.0.1:5002/", osrm.profile = "foot")
route <- osrmRoute(src = origin[1:2], dst = destination[1:2], overview = "full", returnclass = "sf")
route = st_transform(route, crs = st_crs(crs))
track = as.data.frame(cbind(unlist(route$geometry)[1:(length(unlist(route$geometry))/2)], unlist(route$geometry)[((length(unlist(route$geometry))/2)+1):length(unlist(route$geometry))]))