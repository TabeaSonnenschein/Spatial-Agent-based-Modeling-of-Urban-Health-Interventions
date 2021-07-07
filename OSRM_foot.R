pkgs <- c("osrm", "sf")
sapply(pkgs, require, character.only = T) #load 
options(osrm.server = "http://127.0.0.1:5002/", osrm.profile = "foot")
route <- osrmRoute(src = origin[1:2], dst = destination[1:2], overview = "full", returnclass = "sf")
track = as.data.frame(cbind(unlist(route$geometry)[1:(length(unlist(route$geometry))/2)], unlist(route$geometry)[((length(unlist(route$geometry))/2)+1):length(unlist(route$geometry))]))
track_points = paste("{", track[,1], ",", track[,2], ",0}", sep = "")