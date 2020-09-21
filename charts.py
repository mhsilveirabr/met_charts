import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
import numpy as np
from metpy.units import units

from indices import CalculateIndices
from variables import ExtractVariables


class CalculateCharts:
    def __init__(self, data):
        self.data = data
        self.variables = ExtractVariables(self.data)
        self.indices = CalculateIndices(self.data)

        self.area_1 = {'SBSR': (-20.816111, -49.404722),
                       'SBAU': (-21.144167, -50.426389),
                       'SBAQ': (-21.804444, -48.140278),
                       'SBRP': (-21.136389, -47.776667),
                       'SBAX': (-19.560556, -46.965556),
                       'SBUL': (-18.883611, -48.225278),
                       'SBUR': (-19.764722, -47.966111),
                       'SBVG': (-21.588889, -45.473333),
                       'SBZM': (-21.513056, -43.173056),
                       'SBBH': (-19.851944, -43.950556),
                       'SBCF': (-19.624444, -43.971944),
                       'SBMK': (-16.706111, -43.821944),
                       'SBIP': (-19.470556, -42.488056),
                       'SBGV': (-18.896944, -41.986111),
                       'SBBR': (-15.871111, -47.918611),
                       'SBGO': (-16.632500, -49.221111),
                       'SBCN': (-17.724722, -48.610000),
                       'SWLC': (-17.834722, -50.956111),
                       'SBBW': (-15.860833, -52.389444),
                       'SNBR': (-12.079167, -45.009444),
                       'SBLE': (-12.482222, -41.276944),
                       'SBVC': (-14.907778, -40.914722),
                       'SNVB': (-13.296389, -38.992500),
                       'SDIY': (-12.200556, -38.900556),
                       'SBSV': (-12.908611, -38.322500),
                       'SBIL': (-14.815000, -39.033333),
                       'SNTF': (-17.524444, -39.668333)}

        self.area_2 = {'SBGR': (-23.435556, -46.473056),
                       'SBMT': (-23.506667, -46.633889),
                       'SBSP': (-23.626111, -46.656389),
                       'SBSJ': (-23.228889, -45.871111),
                       'SBTA': (-23.038889, -45.515833),
                       'SBST': (-23.928056, -46.299722),
                       'SBKP': (-23.006944, -47.134444),
                       'SBJD': (-23.181667, -46.943611),
                       'SBBP': (-22.979167, -46.537500),
                       'SBJH': (-23.426944, -47.165833),
                       'SDCO': (-23.483056, -47.486389),
                       'SBBU': (-22.343611, -49.053889),
                       'SBAE': (-22.157778, -49.068333),
                       'SBML': (-22.195556, -49.926944),
                       'SBDN': (-22.178333, -51.418889),
                       'SBCR': (-19.011944, -57.671389),
                       'SBCG': (-20.469444, -54.670278),
                       'SBTG': (-20.751389, -51.680278),
                       'SBDB': (-21.247222, -56.452500),
                       'SBDO': (-22.200556, -54.925556),
                       'SBPP': (-22.549722, -55.703056),
                       'SBLO': (-23.330278, -51.136667),
                       'SBMG': (-23.479444, -52.012222),
                       'SBTD': (-24.685278, -53.696389),
                       'SBCA': (-25.002222, -53.501944),
                       'SSGG': (-25.388333, -51.523611),
                       'SBPO': (-26.217222, -52.694444)}
        # Obtain coordinates
        self.lon_2d, self.lat_2d = self.variables.coordinates()

    def create_map(self):
        # Set Projection of Plot
        plotcrs = ccrs.cartopy.crs.Mercator(central_longitude=0.0,
                                            min_latitude=-80.0,
                                            max_latitude=84.0,
                                            globe=None,
                                            latitude_true_scale=None,
                                            false_easting=0.0,
                                            false_northing=0.0,
                                            scale_factor=None)

        # Create new figure
        fig = plt.figure(figsize=(10, 12))
        gs = gridspec.GridSpec(2, 1, height_ratios=[1, .02], bottom=.07, top=.99,
                               hspace=0.01, wspace=0.01)

        # Add the map and set the extent
        ax = plt.subplot(gs[0], projection=plotcrs)

        ax.set_extent([-35., -60., -10., -30.])
        # Add state/country boundaries to plot
        states_provinces = cfeature.NaturalEarthFeature(
            category='cultural',
            name='admin_1_states_provinces_lines',
            scale='50m',
            facecolor='none')

        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS)
        ax.add_feature(states_provinces, edgecolor='gray')
        ax.gridlines(draw_labels=True, dms=True,
                     x_inline=False, y_inline=False)

        # Plot area_1 airports:
        lons_1 = [x[-1] for x in self.area_1.values()]
        lats_1 = [y[0] for y in self.area_1.values()]
        ax.scatter(lons_1, lats_1, transform=ccrs.PlateCarree(), marker="*", c='mediumblue')

        # Plot area_2 airports:
        lons_2 = [x[-1] for x in self.area_2.values()]
        lats_2 = [y[0] for y in self.area_2.values()]
        ax.scatter(lons_2, lats_2, transform=ccrs.PlateCarree(), marker="*", c='indigo')

        return fig, ax

    def clouds_humidity(self):
        """
        UR > 70% average(850, 700, 500) (blue contourf)
        UR > 70% average (1000, 850) (green countour)
        Wind > 5m/s (arrows)
        1000-500mb thickness (red contour)
        Sea level pressure (black contour)
        """
        print('processing')
        # Create figure/map
        fig, ax = self.create_map()

        # UR > 70% average (1000, 850) (green countour)
        rhum_1000 = self.variables.relative_humidity(1000)
        rhum_850 = self.variables.relative_humidity(850)
        rhum_1000_850 = (rhum_1000.values + rhum_850.values) / 2
        # Create plot
        cint = np.arange(rhum_1000_850.min(), rhum_1000_850.max(), 10)
        ax.contourf(self.lon_2d, self.lat_2d, rhum_1000_850,
                    cmap='Greens', transform=ccrs.PlateCarree(),
                    alpha=0.3, levels=cint[cint > 70], extend='max')

        # UR > 70% average(850, 700, 500) (blue contourf)
        rhum_700 = self.variables.relative_humidity(700)
        rhum_500 = self.variables.relative_humidity(500)
        rhum_850_700_500 = (
            rhum_850.values + rhum_700.values + rhum_500.values) / 3
        # Create plot
        cint = np.arange(rhum_850_700_500.min(), rhum_850_700_500.max(), 10)
        ax.contourf(self.lon_2d, self.lat_2d, rhum_850_700_500,
                    cmap='Blues', transform=ccrs.PlateCarree(),
                    alpha=0.3, levels=cint[cint > 70], extend='max')

        # Wind > 5m/s (arrows)
        # uwnd_850, vwnd_850 = self.variables.wind_components(850)
        # # Create plot
        # ax.barbs(self.lon_2d, self.lat_2d, np.array(uwnd_850), np.array(vwnd_850),
        #          length=6, regrid_shape=20, pivot='middle', transform=ccrs.PlateCarree(),
        #          barbcolor='gray')

        # 1000-500mb thickness (red contour)
        hgpt_1000 = self.variables.geopotential_height(1000)
        hgpt_500 = self.variables.geopotential_height(500)
        hgpt_1000_500 = hgpt_500.values - hgpt_1000.values
        # Create plot
        cint = np.arange(hgpt_1000_500.min(), hgpt_1000_500.max(),
                         (hgpt_1000_500.max() - hgpt_1000_500.min()) / 10)
        cs = ax.contour(self.lon_2d, self.lat_2d, hgpt_1000_500, colors='red',
                        transform=ccrs.PlateCarree(), levels=cint, alpha=0.6)
        ax.clabel(cs, inline=True, fontsize=8, fmt='%0.0f')

        # Sea level pressure (black contour)
        mslp = self.variables.mean_sea_level_pressure()
        # Create plot
        cint = np.linspace(mslp.min(), mslp.max())
        cs = ax.contour(self.lon_2d, self.lat_2d, mslp, colors='black',
                        transform=ccrs.PlateCarree(), alpha=0.6)
        ax.clabel(cs, inline=True, fontsize=8, fmt='%0.0f')
        ax.set_title('Umidade e/ou nebulosidade', fontsize=16, ha='center')
        return fig

    def showers_heat_humidity(self):
        """
        K > 30 + TTS > 45 (green countourf)
        K > 30 + TTS > 45 + LI < -1 (red countourf)
        LIFT (blue contour)
        300hPa geopotential height (black contour)
        """
        # Create figure/map
        fig, ax = self.create_map()

        # K > 30 + TTS > 45 (green countourf)
        k_index = self.indices.k()
        tt_index = self.indices.tt()
        condition = (k_index > 30) & (tt_index > 45)
        k_30_tt_45 = (k_index * condition) + (tt_index * condition)
        # Create plot
        ax.contourf(self.lon_2d, self.lat_2d, k_30_tt_45,
                    cmap='Greens', transform=ccrs.PlateCarree(),
                    alpha=0.5)
        # K > 30 + TTS > 45 + LI < -1 (red countourf)
        li_index = self.indices.li()
        condition = (k_index > 30) & (tt_index > 45) & (li_index < -1)
        k_30_tt_45_li_m1 = (k_index * condition) + \
            (tt_index * condition) + (li_index * condition)
        ax.contourf(self.lon_2d, self.lat_2d, k_30_tt_45_li_m1,
                    cmap='Reds', transform=ccrs.PlateCarree(),
                    alpha=0.5)
        # LIFT (blue contour)
        ax.contour(self.lon_2d, self.lat_2d, li_index,
                   colors='blue', transform=ccrs.PlateCarree(),
                   alpha=0.5)
        # 300hPa geopotential height (black contour)
        hgpt_300 = self.variables.geopotential_height(300)
        ax.contour(self.lon_2d, self.lat_2d, hgpt_300,
                   colors='black', transform=ccrs.PlateCarree(),
                   alpha=0.5)
        return fig

    def rain(self):
        """
        OMEGA -0.001 (green contourf)
        OMEGA -0.01 and UR > 40% average(1000/850) (orange contourf)
        OMEGA -0.5 and UR > 70% average(1000/850/700/500) (red contourf)
        500hPa geopotential height (black contour)
        500hPa Streamlines (gray streamlines)
        """

    def thunderstorm_showers(self):
        """
        OMEGA -0.001 and UR > 40% average(1000/500) and K >30 TTS>45 LIF < -1 (red contourf)
        OMEGA -0.001 and UR > 40% average(1000/500) and K >30 TTS>45 (orange contourf)
        250hPa divergence (blue contourf)
        250hPa Streamlines (gray streamlines)
        """

    def storms(self):
        """
        OMEGA -0.001 and UR > 40% average(1000/500) and K >35 TTS>50 LIF < -4 (purple contourf)
        850hPa wind (green contourf)
        850hPa >15m/s wind (vector)
        250hPa jetstream (wind > 35m/s) (yellow contourf)
        Precipitable water 40-60mm (red contour)
        850hPa streamlines (gray streamlines)
        """

    def hail(self):
        """
        OMEGA -0.001 and UR > 70% average(1000/500) and TTS>52 VT > 25 SWEAT>220 LIF < -2 (blue contourf)
        500 hPa temperature (black contour)
        850 hPa temperature (gray contour)
        500hPa OMEGA > -2 (orange contour)
        """

    def instability(self):
        """
        index = ((K > 30) + (TT > 45) + (SWEAT > 220)) / 3
        if index > 1, then unstable
        """

    # def temperature_advection(self):
    #     # Pull out variables you want to use
    #     hght_var = self.data.variables['Geopotential_height_isobaric']
    #     temp_var = self.data.variables['Temperature_isobaric']
    #     u_wind_var = self.data.variables['u-component_of_wind_isobaric']
    #     v_wind_var = self.data.variables['v-component_of_wind_isobaric']
    #     lat_var = self.data.variables['lat']
    #     lon_var = self.data.variables['lon']

    #     # Get actual data values and remove any size 1 dimensions
    #     lat = lat_var[:].squeeze()
    #     lon = lon_var[:].squeeze()
    #     hght = hght_var[:].squeeze()
    #     temp = units.Quantity(temp_var[:].squeeze(), temp_var.units)
    #     u_wind = units.Quantity(u_wind_var[:].squeeze(), u_wind_var.units)
    #     v_wind = units.Quantity(v_wind_var[:].squeeze(), v_wind_var.units)

    #     lev_850 = np.where(self.data.variables['isobaric'][:] == 850 * 100)[0][0]
    #     hght_850 = hght[lev_850]
    #     temp_850 = temp[lev_850]
    #     u_wind_850 = u_wind[lev_850]
    #     v_wind_850 = v_wind[lev_850]

    #     # Combine 1D latitude and longitudes into a 2D grid of locations
    #     lon_2d, lat_2d = np.meshgrid(lon, lat)

    #     # Gridshift for barbs
    #     lon_2d[lon_2d > 180] = lon_2d[lon_2d > 180] - 360

    #     #########################################

    #     # Use helper function defined above to calculate distance
    #     # between lat/lon grid points
    #     dx, dy = mpcalc.lat_lon_grid_deltas(lon_var, lat_var)

    #     # Calculate temperature advection using metpy function
    #     adv = mpcalc.advection(temp_850, [u_wind_850, v_wind_850],
    #                            (dx, dy), dim_order='yx')

    #     # Smooth heights and advection a little
    #     # Be sure to only put in a 2D lat/lon or Y/X array for smoothing
    #     Z_850 = mpcalc.smooth_gaussian(hght_850, 2)
    #     adv = mpcalc.smooth_gaussian(adv, 2)

    #     # Set Projection of Data
    #     datacrs = ccrs.PlateCarree()

    #     # Set Projection of Plot
    #     plotcrs = ccrs.cartopy.crs.Mercator(central_longitude=0.0,
    #                                         min_latitude=-80.0,
    #                                         max_latitude=84.0,
    #                                         globe=None,
    #                                         latitude_true_scale=None,
    #                                         false_easting=0.0,
    #                                         false_northing=0.0,
    #                                         scale_factor=None)

    #     # Create new figure
    #     fig = plt.figure(figsize=(10, 12))
    #     gs = gridspec.GridSpec(2, 1, height_ratios=[1, .02], bottom=.07, top=.99,
    #                            hspace=0.01, wspace=0.01)

    #     # Add the map and set the extent
    #     ax = plt.subplot(gs[0], projection=plotcrs)
    #     # plt.title(f'850mb Temperature Advection for {time:%d %B %Y %H:%MZ}', fontsize=16)
    #     ax.set_extent([-30., -80., 0., -50.])

    #     # Plot Height Contours
    #     clev850 = np.arange(900, 3000, 30)
    #     cs = ax.contour(lon_2d, lat_2d, Z_850, clev850, colors='black', linewidths=1.5,
    #                     linestyles='solid', transform=datacrs)
    #     plt.clabel(cs, fontsize=10, inline=1, inline_spacing=10, fmt='%i',
    #                rightside_up=True, use_clabeltext=True)

    #     # Plot Temperature Contours
    #     clevtemp850 = np.arange(-20, 20, 2)
    #     cs2 = ax.contour(lon_2d, lat_2d, temp_850.to(units('degC')), clevtemp850,
    #                      colors='green', linewidths=1.25, linestyles='dashed',
    #                      transform=datacrs)
    #     plt.clabel(cs2, fontsize=10, inline=1, inline_spacing=10, fmt='%i',
    #                rightside_up=True, use_clabeltext=True)

    #     # Plot Colorfill of Temperature Advection
    #     cint = np.arange(-8, 9)
    #     cf = ax.contourf(lon_2d, lat_2d, 3 * adv.to(units('delta_degC/hour')), cint[cint != 0],
    #                      extend='both', cmap='bwr', transform=datacrs)
    #     cax = plt.subplot(gs[1])
    #     cb = plt.colorbar(cf, cax=cax, orientation='horizontal', extendrect=True, ticks=cint)
    #     cb.set_label(r'$^{o}C/3h$', size='large')

        # # Add state/country boundaries to plot
        # states_provinces = cfeature.NaturalEarthFeature(
        #     category='cultural',
        #     name='admin_1_states_provinces_lines',
        #     scale='50m',
        #     facecolor='none')

        # SOURCE = 'Natural Earth'
        # LICENSE = 'public domain'

        # ax.add_feature(cfeature.LAND)
        # ax.add_feature(cfeature.COASTLINE)
        # ax.add_feature(cfeature.BORDERS)
        # ax.add_feature(states_provinces, edgecolor='gray')
        # ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

        # # Plot Wind Barbs
        # ax.barbs(lon_2d, lat_2d, u_wind_850.magnitude, v_wind_850.magnitude,
        #          length=6, regrid_shape=20, pivot='middle', transform=datacrs)

    #     plt.savefig('test.png')
    #     plt.show()
