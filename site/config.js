/* Find a Mass settings.

   mapStyleUrl: the street map. OpenFreeMap is free, needs no account or key,
   and has no limits on map views. Its styles:
     https://tiles.openfreemap.org/styles/liberty    detailed and colourful (default)
     https://tiles.openfreemap.org/styles/bright     classic road-map colours
     https://tiles.openfreemap.org/styles/positron   pale and minimal, so pins stand out most
   Any other MapLibre style URL also works (for example from MapTiler or Stadia Maps).
   If the style can't load, the app switches to OpenStreetMap's standard map automatically.
   Set it to '' to always use that OpenStreetMap map. */
window.FIND_A_MASS_CONFIG = {
  mapStyleUrl: 'https://tiles.openfreemap.org/styles/liberty',
};
