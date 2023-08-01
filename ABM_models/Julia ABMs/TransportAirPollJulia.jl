using Agents
using DataFrames
using GeoDataFrames
using Dates
#using PMML
using Random
using Statistics
using Query
using LightGBM
using HTTP
using LibGEOS: LineString

const crs = "epsg:28992"  # Replace this with your desired coordinate reference system

@agent Humans OSMAgent begin
    # socio-demographic attributes
    unique_id::Int
    Neighborhood::Int
    current_edu::String
    IndModalPreds::Vector{Int}
    ScheduleID::Int
    MondaySchedule::Vector{Int}
    TuesdaySchedule::Vector{Int}
    WednesdaySchedule::Vector{Int}
    ThursdaySchedule::Vector{Int}
    FridaySchedule::Vector{Int}
    SaturdaySchedule::Vector{Int}
    SundaySchedule::Vector{Int}
    former_activity::Int
    activity::String

    # regular destinations
    Residence::NTuple{2, Float64}
    University::NTuple{2, Float64}
    School::NTuple{2, Float64}
    Workplace::NTuple{2, Float64}

    # mobility behavior variables
    path_memory::Int
    traveldecision::Int
    #thishourtrack::Vector{LineString{Float64}}
    thishourmode::Vector{String}
    modalchoice::String
    arrival_time::DateTime
    track_geometry::LineString{Float64}
    track_duration::Float64
    trip_distance::Float64
   # nexthourstracks::Vector{LineString{Float64}}
    nexthoursmodes::Vector{String}
end

function Humans(vector::Vector, model::Model)
    unique_id = vector[1]
    Neighborhood = vector[2]
    current_edu = vector[9]
    IndModalPreds = [vector[i] for i in [19, 2, 13, 20, 21, 22, 17, 11, 12, 5, 7, 15, 14, 16]]
    ScheduleID = vector[18]
    MondaySchedule = model.scheduledf_monday |> @filter(_.ScheduleID == ScheduleID) |> first |> row -> row[2:end]
    TuesdaySchedule = model.scheduledf_tuesday |> @filter(_.ScheduleID == ScheduleID) |> first |> row -> row[2:end]
    WednesdaySchedule = model.scheduledf_wednesday |> @filter(_.ScheduleID == ScheduleID) |> first |> row -> row[2:end]
    ThursdaySchedule = model.scheduledf_thursday |> @filter(_.ScheduleID == ScheduleID) |> first |> row -> row[2:end]
    FridaySchedule = model.scheduledf_friday |> @filter(_.ScheduleID == ScheduleID) |> first |> row -> row[2:end]
    SaturdaySchedule = model.scheduledf_saturday |> @filter(_.ScheduleID == ScheduleID) |> first |> row -> row[2:end]
    SundaySchedule = model.scheduledf_sunday |> @filter(_.ScheduleID == ScheduleID) |> first |> row -> row[2:end]
    former_activity = TuesdaySchedule[model.activitystep + 1]
    activity = "perform_activity"

    # regular destinations
    try
        Residence = model.Residences |> @filter(_.nghb_cd == Neighborhood) |> first |> row -> row.geometry |> getcentroid |> coords |> first
    catch
        Residence = model.Residences |> getcentroid |> coords |> first
    end
    if current_edu == "high"
        University = model.Universities |> getcentroid |> coords |> first
    else
        School = nearest_points(Point(Residence), model.Schools |> getgeometrys |> unaryunion)[2] |> coords |> first
    end
    if 3 in vcat(MondaySchedule, TuesdaySchedule, WednesdaySchedule, ThursdaySchedule, FridaySchedule, SaturdaySchedule, SundaySchedule)
        Workplace = model.Profess |> getcentroid |> coords |> first
    end

    # mobility behavior variables
    path_memory = 0
    traveldecision = 0
    #thishourtrack = Vector{LineString{Float64}}()
    thishourmode = Vector{String}()
    modalchoice = ""
    arrival_time = DateTime(0)
    #track_geometry = LineString{Float64}()
    track_duration = 0.0
    trip_distance = 0.0
    #nexthourstracks = Vector{LineString{Float64}}()
    nexthoursmodes = Vector{String}()

    Humans(
        unique_id, Neighborhood, current_edu, IndModalPreds, ScheduleID,
        MondaySchedule, TuesdaySchedule, WednesdaySchedule, ThursdaySchedule, FridaySchedule,
        SaturdaySchedule, SundaySchedule, former_activity, activity, Residence, University,
        School, Workplace, path_memory, traveldecision, thishourtrack, thishourmode,
        modalchoice, arrival_time, track_geometry, track_duration, trip_distance,
        nexthourstracks, nexthoursmodes,
    )
end

function ScheduleManager!(agent::Humans)
    # identifying the current activity
    if model.weekday == 0
        agent.activity = model.scheduledf_monday[agent.ScheduleID][model.activitystep + 1]
    elseif model.weekday == 1
        agent.activity = model.scheduledf_tuesday[agent.ScheduleID][model.activitystep + 1]
    elseif model.weekday == 2
        agent.activity = model.scheduledf_wednesday[agent.ScheduleID][model.activitystep + 1]
    elseif model.weekday == 3
        agent.activity = model.scheduledf_thursday[agent.ScheduleID][model.activitystep + 1]
    elseif model.weekday == 4
        agent.activity = model.scheduledf_friday[agent.ScheduleID][model.activitystep + 1]
    elseif model.weekday == 5
        agent.activity = model.scheduledf_saturday[agent.ScheduleID][model.activitystep + 1]
    elseif model.weekday == 6
        agent.activity = model.scheduledf_sunday[agent.ScheduleID][model.activitystep + 1]
    end



    # Identifying whether activity changed and if so, where the new activity is located and whether we have a saved route towards that destination
    if agent.current_activity != agent.former_activity
        if agent.current_activity == 3  # 3 = work
            agent.commute = 1
            agent.destination_activity = agent.Workplace
            if haskey(agent, :homeTOwork) && (agent.former_activity == 5 || agent.former_activity == 1)  # 1 = sleep/rest, 5 = at home
                agent.track_path = agent.homeTOwork
                agent.track_geometry = agent.homeTOwork_geometry
                agent.modalchoice = agent.homeTOwork_mode
                agent.track_duration = agent.homeTOwork_duration
                agent.path_memory = 1
                println("saved pathway")
            end
        elseif agent.current_activity == 4  # 4 = school/university
            agent.edu_trip = 1
            if agent.current_edu == "high"
                agent.destination_activity = agent.University
            else
                agent.destination_activity = agent.School
            end
            # 1 = sleep/rest, 5 = at home, 6 = cooking
            if haskey(agent, :homeTOschool_geometry) && (agent.former_activity in [5, 1, 6, 7])
                agent.track_geometry = agent.homeTOschool_geometry
                agent.modalchoice = agent.homeTOschool_mode
                agent.track_duration = agent.homeTOschool_duration
                agent.path_memory = 1
                println("saved pathway")
            end
        elseif agent.current_activity == "groceries_shopping"
            agent.destination_activity = agent.Supermarket
            agent.groceries = 1
            # 1 = sleep/rest, 5 = at home, 6 = cooking
            if haskey(agent, :homeTOsuperm_geometry) && (agent.former_activity in [5, 1, 6, 7])
                agent.track_geometry = agent.homeTOsuperm_geometry
                agent.track_duration = agent.homeTOsuperm_duration
                agent.modalchoice = agent.homeTOsuperm_mode
                agent.path_memory = 1
                println("saved pathway")
            end
        elseif agent.current_activity == "kindergarden"
            agent.destination_activity = agent.Kindergarden
            # 1 = sleep/rest, 5 = at home, 6 = cooking
            if haskey(agent, :homeTOkinderga_geometry) && (agent.former_activity in [5, 1, 6, 7])
                agent.track_geometry = agent.homeTOkinderga_geometry
                agent.track_duration = agent.homeTOkinderga_duration
                agent.modalchoice = agent.homeTOkinderga_mode
                agent.path_memory = 1
                println("saved pathway")
            end
        elseif agent.current_activity in [5, 1, 6, 7]
            agent.destination_activity = agent.Residence
            if haskey(agent, :workTOhome_geometry) && agent.former_activity == 3  # 3 = work
                agent.track_geometry = agent.workTOhome_geometry
                agent.modalchoice = agent.homeTOwork_mode
                agent.track_duration = agent.homeTOwork_duration
                agent.path_memory = 1
                println("saved pathway_ return")
            elseif haskey(agent, :schoolTOhome_geometry) && agent.former_activity == 4  # 4 = school/university
                agent.track_geometry = agent.schoolTOhome_geometry
                agent.modalchoice = agent.homeTOschool_mode
                agent.track_duration = agent.homeTOschool_duration
                agent.path_memory = 1
                println("saved pathway_ return")
            elseif haskey(agent, :supermTOhome_geometry) && agent.location == agent.Supermarket
                agent.track_geometry = agent.supermTOhome_geometry
                agent.modalchoice = agent.homeTOsuperm_mode
                agent.track_duration = agent.homeTOsuperm_duration
                agent.path_memory = 1
                println("saved pathway_ return")
            elseif haskey(agent, :kindergaTOhome_geometry) && agent.location == agent.Kindergarden
                agent.track_geometry = agent.kindergaTOhome_geometry
                agent.modalchoice = agent.homeTOkinderga_mode
                agent.track_duration = agent.homeTOkinderga_duration
                agent.path_memory = 1
                println("saved pathway_ return")
            end
        elseif agent.current_activity == 11
            agent.leisure = 1
            agent.destination_activity = model.Entertainment["geometry"].sample(1).values[1]
        elseif agent.current_activity == 2  # 2 = eating
            if any(model.Restaurants["geometry"].within(Point(tuple(agent.pos)).buffer(500)))
                agent.nearRestaurants = model.Restaurants["geometry"].intersection(Point(tuple(agent.pos)).buffer(500))
                agent.destination_activity = agent.nearRestaurants[~agent.nearRestaurants.is_empty].sample(1).values[1]
            else
                agent.destination_activity = [(p.x, p.y) for p in nearest_points(Point(tuple(agent.pos)), model.Restaurants["geometry"].unary_union)][2]
            end
            
        if agent.destination_activity != agent.pos
            if agent.path_memory != 1
                agent.traveldecision = 1
                agent.route_eucl_line = LineString([Point(agent.pos), Point(agent.destination_activity)])
                agent.trip_distance = get_distance_meters(agent.pos[1], agent.pos[2], agent.destination_activity[1], agent.destination_activity[2], project_to_WSG84)
            else
                agent.activity = "traveling"
                agent.arrival_time = model.current_datetime + Dates.Minute(agent.track_duration)
                AssignTripToTraffic(agent)
            end
            agent.path_memory = 0
        else
            agent.activity = "perform_activity"
            agent.traveldecision = 0
        end
    end
end


function PerceiveEnvironment(agent::Humans, model::Model)
    # Variables to be joined to route
    route_geo_df = GeoDataFrame(data = Dict("id" => ["1"], "geometry" => [agent.route_eucl_line]), crs = crs)
    agent.RouteVars = GeoDataFrame(sjoin(route_geo_df, agent.model.EnvBehavDeterms, how = "left"))[agent.model.routevariables].mean(axis = 1)

    # Variables to be joined to current location
    pos_point = Point(agent.pos)
    orig_geo_df = GeoDataFrame(data = Dict("id" => ["1"], "geometry" => [pos_point]), crs = crs)
    agent.OrigVars = GeoDataFrame(sjoin(orig_geo_df, agent.model.EnvBehavDeterms, how = "left"))[agent.model.originvariables][1]

    # Variables to be joined to destination
    dest_point = Point(agent.destination_activity)
    dest_geo_df = GeoDataFrame(data = Dict("id" => ["1"], "geometry" => [dest_point]), crs = crs)
    agent.DestVars = GeoDataFrame(sjoin(dest_geo_df, agent.model.EnvBehavDeterms, how = "left"))[agent.model.destinvariables][1]
end

function ModeChoice(agent::Humans, model::Model)
    pred_data = hcat(agent.RouteVars, agent.OrigVars, agent.DestVars, agent.IndModalPreds, [agent.trip_distance])
    pred_df = DataFrame(pred_data', names(agent.model.routevariables_suff, agent.model.originvariables_suff, agent.model.destinvariables_suff, agent.model.personalvariables, agent.model.tripvariables), 1)
    replace_dict = Dict("1" => "bike", "2" => "drive", "3" => "transit", "4" => "walk")
    agent.modechoice = replace(string(predict(agent.model.ModalChoiceModel, pred_df[agent.model.OrderPredVars])[1]), replace_dict)
end

# OSRM Routing Machine
function Routing(agent::Humans)
    mode_server_dict = Dict("bike" => "http://127.0.0.1:5001/", "drive" => "http://127.0.0.1:5000/", "walk" => "http://127.0.0.1:5002/", "transit" => "http://127.0.0.1:5002/")
    mode_lua_profile_dict = Dict("bike" => "bike", "drive" => "car", "walk" => "foot", "transit" => "foot")
    
    agent.lua_profile = mode_lua_profile_dict[agent.modechoice]
    agent.server = mode_server_dict[agent.modechoice]
      
    orig_point = transform(project_to_WSG84, Point(agent.pos))
    dest_point = transform(project_to_WSG84, Point(agent.destination_activity))
    url = string(agent.server, "route/v1/", agent.lua_profile, "/", orig_point.x, ",", orig_point.y, ";", dest_point.x, ",", dest_point.y, "?overview=full&geometries=polyline")
    res = HTTP.get(url).body |> JSON.parse
    agent.track_geometry = transform(projecy_to_crs, transform(flip, LineString(polyline.decode(res["routes"][1]["geometry"]))))
    agent.track_duration = res["routes"][1]["duration"] / 60  # minutes
    if agent.modechoice == "transit"
        agent.track_duration /= 10
    end
    agent.trip_distance = res["routes"][1]["distance"]  # meters
end

function SavingRoute(agent::Humans)
    if agent.former_activity in [5, 1, 6, 7]
        if agent.current_activity == 3
            agent.homeTOwork_mode = agent.modechoice
            agent.homeTOwork_geometry = agent.track_geometry
            agent.homeTOwork_duration = agent.track_duration
            agent.workTOhome_geometry = reverse_geom(agent.track_geometry)
        elseif agent.current_activity == 4
            agent.homeTOschool_mode = agent.modechoice
            agent.homeTOschool_geometry = agent.track_geometry
            agent.homeTOschool_duration = agent.track_duration
            agent.schoolTOhome_geometry = reverse_geom(agent.track_geometry)
        elseif agent.current_activity == "kindergarden"
            agent.homeTOkinderga_mode = agent.modechoice
            agent.homeTOkinderga_geometry = agent.track_geometry
            agent.homeTOkinderga_duration = agent.track_duration
            agent.kindergaTOhome_geometry = reverse_geom(agent.track_geometry)
        elseif agent.current_activity == "groceries_shopping"
            agent.homeTOsuperm_mode = agent.modechoice
            agent.homeTOsuperm_geometry = agent.track_geometry
            agent.homeTOsuperm_duration = agent.track_duration
            agent.supermTOhome_geometry = reverse_geom(agent.track_geometry)
        end
    end
end

function TravelingAlongRoute(agent::Humans)
    if agent.model.current_datetime >= agent.arrival_time
        agent.activity = "perform_activity"
        agent.pos = agent.destination_activity
    end
end

function AssignTripToTraffic(agent::Humans)
    if agent.arrival_time.hour != agent.model.hour
        println("multihour trip")
        track_length = agent.track_geometry.length
        agent.trip_segments = [((60 - agent.model.minute) / agent.track_duration)]
        if 60 / (agent.track_duration - (60 - agent.model.minute)) < 1
            agent.trip_segments.extend(list(it.repeat(60 / agent.track_duration, Int((agent.track_duration - (60 - agent.model.minute)) / 60))))
        end
        agent.segment_geometry = [agent.track_geometry]
        for x in agent.trip_segments
            agent.segment_geometry.extend(split(snap(agent.segment_geometry[end], agent.segment_geometry[end].interpolate(x * track_length), 10), agent.segment_geometry[end].interpolate(x * track_length)).geoms)
        end
        agent.segment_geometry = [agent.segment_geometry[x] for x in list(range(1, length(agent.segment_geometry) - 1, 2)) + [length(agent.segment_geometry) - 1]]
        push!(agent.thishourtrack, agent.segment_geometry[1])
        push!(agent.thishourmode, agent.modechoice)
        agent.nexthourstracks = agent.segment_geometry[2:end]
        agent.nexthoursmodes = list(it.repeat(agent.modechoice, length(agent.nexthourstracks)))
    else
        push!(agent.thishourtrack, agent.track_geometry)
        push!(agent.thishourmode, agent.modechoice)
    end
end

function AtPlaceExposure(agent)
    # Placeholder function, do nothing
end

function TravelExposure(agent::Humans)
    thishourtrack_gdf = GeoDataFrame(data = Dict("id" => 1:length(agent.thishourtrack), "geometry" => agent.thishourtrack), crs = crs)
    thishourtrack_gdf = overlay(thishourtrack_gdf, agent.model.AirPollGrid, how = "intersection")
    thishourtrack_gdf["length"] = length.(thishourtrack_gdf.geometry)
    println(thishourtrack_gdf["length"])
    thishourtrack_gdf.plot()
    agent.thishourmode = [agent.nexthoursmodes[1]]
    agent.thishourtrack = [agent.nexthourstracks[1]]
    agent.nexthourstracks = agent.nexthourstracks[2:end]
    agent.nexthoursmodes = agent.nexthoursmodes[2:end]
end

function step!(agent::Humans, model::TransportAirPollutionExposureModel)
    # Schedule Manager
    if model.minute % 10 == 0 || model.minute == 0
        ScheduleManager!(agent, model)
    end

    # Travel Decision
    if agent.traveldecision == 1
        PerceiveEnvironment!(agent, model)
        ModeChoice!(agent, model)
        Routing!(agent, model)
        SavingRoute!(agent, model)
        agent.arrival_time = model.current_datetime + Dates.Minute(agent.track_duration)
        agent.activity = "traveling"
        agent.traveldecision = 0
        AssignTripToTraffic!(agent)
    end

    if agent.activity == "traveling"
        TravelingAlongRoute!(agent, model)
    end
end

# Export the agent definition
@agent Humans


# Define the TransportAirPollutionExposureModel as a function instead of a class in Julia
function initialize(nb_humans, path_data, crs="epsg:28992";
                                                starting_date=DateTime(2019, 1, 1, 6, 50, 0),
                                                steps_minute=10, modelrunname="intervention_scenario")

    # Insert the global definitions, variables, and actions here
    # Define the global variables
    starting_datetime = starting_date
    steps_minute = Dates.Minute(steps_minute)
    current_datetime = starting_date
    minute = Dates.minute(current_datetime)
    weekday = Dates.dayofweek(current_datetime)
    hour = Dates.hour(current_datetime)

   
    temperature = monthly_weather_df[monthly_weather_df[:, :month] .== Dates.month(current_datetime), :Temperature][1]
    winddirection = monthly_weather_df[monthly_weather_df[:, :month] .== Dates.month(current_datetime), :Winddirection][1]
    windspeed = monthly_weather_df[monthly_weather_df[:, :month] .== Dates.month(current_datetime), :Windspeed][1]
    rain = monthly_weather_df[monthly_weather_df[:, :month] .== Dates.month(current_datetime), :Rain][1]
    tempdifference = monthly_weather_df[monthly_weather_df[:, :month] .== Dates.month(current_datetime), :TempDifference][1]


    # Read the Mode of Transport Choice Model
    println("Reading Mode of Transport Choice Model")
    #ModalChoiceModel = load(PMMLTreeClassifier, path_data * "ModalChoiceModel/modalChoice.pmml")
    # Add other data loading and initialization steps as necessary

    space = GridSpaceSingle((20,20), periodic = false)
    model = UnremovableABM(Humans, space; properties = properties, scheduler = Schedulers.randomly)

    # Create the agent population
    println("Creating Agents")
    println(now())
    for i in 1:nb_humans
        # Generate agent attributes and create the agent
        x = rand(1:100)  # Replace this with your actual agent initialization logic
        y = rand(1:100)  # Replace this with your actual agent initialization logic
        agent = MyAgent(i, x, y)
        add_agent!(agent_population, agent)
    end
    println(now())

    # Define the model step function
    function step_model!(model)
        # Manage time variables
        model.current_datetime += model.steps_minute
        println(model.current_datetime)
        model.minute = Dates.minute(model.current_datetime)
        if model.minute == 0  # new hour
            println("Current time: ", model.current_datetime)
            model.hour = Dates.hour(model.current_datetime)
        end
        model.activitystep = (model.hour * 6) + (model.minute ÷ 10)
        if Dates.hour(model.current_datetime) == 0  # new day
            model.weekday = Dates.dayofweek(model.current_datetime)
        end
        if Dates.day(model.current_datetime) == 1 && Dates.hour(model.current_datetime) == 0  # new month
            # Call the function to determine weather
            DetermineWeather(model)
        end

        # Call the appropriate functions for different steps
        # TrafficAssignment(model)
        # OnRoadEmission(model)
        # OffRoadDispersion(model)

        # Advance the model by stepping through the agent population
        for agent in agent_population
            # Update agent behaviors here
        end
    end

    # Define the function to determine weather
    function DetermineWeather(model)
        model.temperature = model.monthly_weather_df[model.monthly_weather_df.month .== Dates.month(model.current_datetime), :Temperature][1]
        model.winddirection = model.monthly_weather_df[model.monthly_weather_df.month .== Dates.month(model.current_datetime), :Winddirection][1]
        model.windspeed = model.monthly_weather_df[model.monthly_weather_df.month .== Dates.month(model.current_datetime), :Windspeed][1]
        model.rain = model.monthly_weather_df[model.monthly_weather_df.month .== Dates.month(model.current_datetime), :Rain][1]
        model.tempdifference = model.monthly_weather_df[model.monthly_weather_df.month .== Dates.month(model.current_datetime), :TempDifference][1]
        println("temperature: ", model.temperature, " rain: ", model.rain, " wind: ", model.windspeed, " wind direction: ", model.winddirection, " tempdifference: ", model.tempdifference)
    end

    # Define the main model loop
    function run_model(model, num_steps)
        for i in 1:num_steps
            step_model!(model)
            # Add any data collection or visualization code here
        end
    end

    # Return the model and agent population
    return agent_population
end


# Define path_data
path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"

# Synthetic Population
println("Reading Population Data")
nb_humans = 400
pop_df = CSV.read(path_data * "Population/Agent_pop_clean.csv")
random_subset = pop_df[rand(1:size(pop_df, 1), nb_humans), :]
CSV.write(path_data * "Population/Amsterdam_population_subset.csv", random_subset, writeheader=true)

# Coordinate Reference System and CRS transformers
crs = "epsg:28992"
using CoordinateTransformations
project_to_WSG84 = Transformer(crs, "epsg:4326", always_xy=true)
projecy_to_crs = Transformer("epsg:4326", crs, always_xy=true)
project_to_meters = Transformer(crs, "epsg:3857")
project_to_latlng = Transformer("epsg:3857", crs, always_xy=true)


 # Load the spatial built environment
 buildings = GeoDataFrame(readfeather(path_data * "FeatherDataABM/Buildings.feather"))
 streets = GeoDataFrame(readfeather(path_data * "FeatherDataABM/Streets.feather"))
 # Add other dataframes for spatial data

# Read the Environmental Stressor Data and Model
AirPollGrid = GeoDataFrame(readfeather(path_data * "FeatherDataABM/AirPollgrid50m.feather"))

 # Load Weather data and set initial weather conditions
 monthly_weather_df = DataFrame(CSV.File(path_data * "Weather/monthlyWeather2019TempDiff.csv"))

# Start OSRM Servers
println("Starting OSRM Servers")
run(`C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/start_OSRM_Servers.bat`)

# Create and run the model with the specified parameters
model = transport_air_pollution_exposure_model(nb_humans, path_data)

# Run the model for a specified number of steps
num_steps = 10  # Replace with the desired number of steps
run_model(model, num_steps)