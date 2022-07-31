# TeslaTrack
Tesla tracker with geofencing and notification

***WIP***

This uses the TeslaPy module and requires OAUTH authentication with the tesla servers.

N.B. The TeslaPy module seems to be built for 'api_version'>=4.x and doesn't work so well with older cars (e.g., 2014 ModelS is currently at 'api_version'=3.6).  The module's behavior with lower api versions is unpredictable (e.g., sometimes it returns data from another of the list of vehicles).

**TODO**
* Fork TeslaPy and make it work for 'api_version'<4.x
* Find an authentication mechanism that runs on linux
* Create web-based interface
* Integrate with maps -- current locations, regions display/define, etc.

**Design Notes**
* key features
  - enumerate all vehicles -- select (proper) subset of them to track
  - report information on current status of selected vehicles
  - refer to vehicles by friendly names -- i.e. <Vehicle>['display_name']
  - define events and notifications
  - run server in background, interact with it through cmd interpreter and web interface
* Command Interpreter
  - choose (proper) subset of selected vehicles to operate on
  - print various (formatted) bits of the vehicle information
  - use jsonPath to extract different parts of the info across multiple vehicles
* Web Interface
  - use maps to plot location, show trigger regions
* Tracker
  - one per selected vehicle (for failure indepencence and concurrency -- maybe for dynamic start/stop too)
  - takes list of triggers and generates notification events of the desired type
  - uses different notification mechanisms
  - register/unregister triggers -- or restart and give it triggers at start?
* Triggers -- things that generate notifications
  - Trigger Events
    * location enters/exits a defined Trigger Region
    * value goes outside of a defined range of values
    * location changes by at least some delta
    * value changes by at least some delta
    * example events:
      - odometer increased by <delta> over last odometer event
      - odometer exceeds <value>
      - climate outside range (<minTemp>, <maxTemp>)
      - climate changes by <deltaValue>
      - 'shift_state' change
      - 'shift_state' transition (<fromState>, <toState>) ???? not like the others ????
      - vehicle enters <region>
      - vehicle exits <region>
  - Trigger Regions:
    * point: (lat,lon)
    * circle: (lat, lon, radius)
    * polygon: [(lat,lon), ...]
* Notifications
  - different types: e.g.,
    * log
    * SMS
    * push notifications to mobile app
    * email
  - same interface (ABC/Protocol)
  - associated with triggers, can have multiple notifications associated with a given trigger instance
