# A tiny blood-glucose monitoring screen

![screen](screen.jpg)

This feels too niche for even me to write about. The odds of anybody else in the world having exactly this collision of interests and circumstances seem ridiculous. And yet...

## Type-1 diabetes

I have [type-1 diabetes](https://www.nhs.uk/conditions/type-1-diabetes/) which means I need to monitor my blood-glucose levels. These days, I use a [Freestyle Libre](https://www.freestyle.abbott/uk-en/home.html)
 stuck to the back of my arm, which connects to my phone over bluetooth, where I can read my score (with ~20 minutes latency. And it's actually a proxy for my blood-glucose, not the real value. But I digress).

 This works fine but I've always found it a little frustrating to have to unlock my phone and open the app to see the data, especially in the middle of the night.

I'm also aware that you can just buy a Freestyle Libre if you want to cosplay being diabetic but I don't understand why you would want to do that.

 ## Enter Home Assistant

 [Home Assistant](https://www.home-assistant.io/) is a great way to automate your home in a way that's _just_ reliable enough to be useful, but flaky enough that occasionally you'll get yelled at because the lights aren't working.

I recently spotted, on a [completely unrelated Mastodon post](https://mastodon.me.uk/deck/@julianlawson@beige.party/114433157512345061), that somebody had their BG score on a Home Assistant dashboard. Upon digging into this further, I learned about [this HA integration](https://github.com/gillesvs/librelink), which hits up the Freestyle Libre API (which I didn't even know was publicly available). And then this data is exposed via the Home Assistant API. So suddenly I have an API on my blood-sugar. Those who know me will understand why this pushed a lot of my buttons.

## Tiny screen

I've [written about my adventures with the st7789v2 screen elsewhere](https://sam.pikesley.org/projects/st7789v2-micropython/), and this seemed like the perfect display for this project. I tweaked the client code from that project (the clock thing was only ever a demo, really) to display some [nicer, easier-to-read-in-the-night numbers](https://github.com/pikesley/bloodstorm/blob/main/st7789v2/conf/font.py), then lashed together a [very noddy API client](https://github.com/pikesley/bloodstorm/blob/main/blood.py#L46) and here we are.

## Using it

I genuinely, 100% do not believe that anybody else will ever do this, but just in case...

You'll need:

* An [m5stack st7789v2 LCD screen](https://thepihut.com/products/lcd-unit-1-14-135-240-pixels-display)
* An [esp32](https://www.ebay.co.uk/itm/276508444371)
  * Be careful here though, lots of the super-minis seem to have broken wifi
* (Optionally) some Lego

Then:
* Connect the red and black cables to 5v and ground on the esp32, and the yellow and white i2c cables to pins 8 and 9 (presuming you have a C3 super-mini. If you've read this far I presume you know what you're doing and can find the right pins. You'll also need to tweak the values in [`conf.py`](https://github.com/pikesley/bloodstorm/blob/main/st7789v2/conf/conf.py))
* Create a file in the root of this directory called `secrets.py` that looks like this:

```python
SSID = "your-wifi-network"
KEY = "your-wifi-password"
BEARER_TOKEN = "your-ha-api-token"  # you can get this from http://homeassistant.local:8123/profile/security or so
HA_HOST = "http://homeassistant.local:8123"
SENSOR_ID = "sensor.your_name_glucose_measurement"  # these entities are under the `librelink` HA integration
TREND_ID = "sensor.your_name_trend"
```

> Once again, if you're still reading, I presume you know how to wrangle an API token out of HA

And then, with the esp32 plugged in to your laptop, run:

```
make push connect
```

Hit `ctrl-D` to reboot, and you should see some numbers.

There's eleventy-billion ways this could fail for you, but as I said, I don't believe anybody else will ever use this so `¯\_(ツ)_/¯`
