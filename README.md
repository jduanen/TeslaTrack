# TeslaTrack
Tesla tracker with geofencing and notification

This uses the TeslaPy module and requires OAUTH authentication with the tesla servers.

N.B. The TeslaPy module seems to be built for 'api_version'>=4.x and doesn't work so well with older cars (e.g., 2014 ModelS is currently at 'api_version'=3.6).  The module's behavior with lower api versions is unpredictable (e.g., sometimes it returns data from another of the list of vehicles).

**TODO**
* Fork TeslaPy and make it work for 'api_version'<4.x
* Find an authentication mechanism that runs on linux
* Create web-based interface

**Design Notes**
* key features
  - enumerate all vehicles
  - report information on current status of selected vehicles
  - refer to vehicles by friendly names -- i.e. <Vehicle>['display_name']
  - define events and notifications
    * vehicle events:
      - odometer increased by <delta> over last odometer event
      - odometer exceeds <value>
      - climate outside range (<minTemp>, <maxTemp>)
      - 'shift_state' change
      - 'shift_state' transition (<fromState>, <toState>)
      - vehicle enters <region>
      - vehicle exists <region>
  - run server in background, interact with it through cli and web interface
