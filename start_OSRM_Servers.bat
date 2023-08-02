start /min cmd /c "cd C:\Users\Tabea\Documents\GitHub\osrm-backend & osrm-routed --algorithm=MLD --threads=1 --port=5000 noord-holland-latest_car.osrm  & pause"
start /min cmd /c "cd C:\Users\Tabea\Documents\GitHub\osrm-backend & osrm-routed --algorithm=MLD --threads=1 --port=5001 noord-holland-latest_bike.osrm & pause"
start /min cmd /c "cd C:\Users\Tabea\Documents\GitHub\osrm-backend & osrm-routed --algorithm=MLD --threads=1 --port=5002 noord-holland-latest_foot.osrm & pause"
exit