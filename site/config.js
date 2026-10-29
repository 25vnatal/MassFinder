/* Find a Mass settings.
   maptilerKey: your MapTiler API key (https://cloud.maptiler.com/account/keys/).
   Restrict the key to your site's address in MapTiler so others can't use it.
   Leave it empty to use the plain district map, which needs no key.
   If the repository has a MAPTILER_KEY variable, the deploy workflow fills this in for you. */
window.FIND_A_MASS_CONFIG = {
  maptilerKey: '',
  mapStyle: 'streets-v2',
  mapStyleDark: 'streets-v2-dark',
};
