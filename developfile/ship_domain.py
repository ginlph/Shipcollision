#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: ship_domain.py
@time: 2019-11-07 21:54
"""

import numpy as np
from matplotlib import pyplot as plt
from math import pi, cos, sin
from matplotlib.path import Path
from matplotlib.patches import PathPatch

'''
This work is based on ship safety domains approach.

The term of a ship domain was ﬁrst introduced in (Fuji, 1971)
definition: a two-dimensional area surrounding a 
        ship which other ships must avoid – it may be considered as the area of evasion.
Parameters: 
    coordinate
        ship_latitude: 
        ship_longtitude:
    sog: Speed over ground (knots)	
    cog: Course over ground (degrees)
-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*    
* method 1   Fuji
*    name     |   description in Ellipse |  description in ship
*    ownship_x:  x-position of the center,    longitude
*    ownship_y:  y-position of the center,    latitude
*    domain_a :  semi-major axis,             7*length
*    domain_b :  semi-minor axis,             3.5*length
*    cog:      rotation angle,              cog
*    

* method 2   Goodwin
*    Thita: the relative bearing of other ships 
*    Sector 1 (starboard sector) 0  <= Thita <= 112.5 
*    Sector 2 (port sector)      247.5 <= Thita < 360 
*    Sector 3 (astern sector)    112.5 <= Thita < 247.5
*    Ref. 
*    [1] Goodwin, E. (1975). A Statistical Study of Ship Domains. Journal of Navigation, 28(3), 328-344. 

* method 3   wang
*    Vown: the own ship speed represented in knots.
*    IQSDk = {(x,y) | fk(x,y;Q) <= 1, Q = {R_fore, R_aft, R_starb, R_port}, k >= 1 }
*    fk(x,y;Q) = ((2 * x) / ((1 + sgnx) * R_fore - (1 - sgnx) * Raft))^k
*              + ((2 * y) / ((1 + sgny) * R_starb - (1 - sgny) * R_port))^k
*    sgnx  = 1 or -1 (x>=0, else )
*    # 
*        / R_fore = (1 + 1.34 * ( K_AD^2 + (K_DT/2)^2)^1/2 ) * L
*        | R_aft = (1 + 0.67 * ( K_AD^2 + (K_DT/2)^2)^1/2 ) * L
*        | R_starb = (0.2 + K_DT) * L
*        \ R_port = (0.2 + 0.75 * K_DT) * L
*    
*    K_AD = AD/L = 10^(0.3591lgVown+0.0952)
*    K_DT = DT/L = 10^(0.5441lgVown-0.0795)
*    # 
*    Ref. list  
*        [1] Wang, N., 2013. A novel analytical framework for dynamic quaternion ship domains.J. Navig. 66, 265–281.
-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
'''
from matplotlib.patches import Ellipse

def fujidomain(own_ship_xy, length, cog=0):
    """
    Parameters
    ----------
    own_ship_xy : (float, float)
        xy coordinates of ellipse centre.
    domain_a : float
        Total length (diameter) of horizontal axis.
    domain_b : float
        Total length (diameter) of vertical axis.
    cog : scalar, optional
        Rotation in degrees anti-clockwise.
    """
    domain_b = 7 * length
    domain_a = 3.5 * length
    t_rot = pi * cog / 180
    t = np.linspace(0, 2 * pi, 100)
    Ell = np.array([domain_a * np.cos(t), domain_b * np.sin(t)])
    R_rot = np.array([[cos(t_rot), sin(t_rot)], [-sin(t_rot), cos(t_rot)]])
    Ell_rot = np.zeros((2, Ell.shape[1]))
    for i in range(Ell.shape[1]):
        Ell_rot[:, i] = np.dot(R_rot, Ell[:, i])
    domain_path = [own_ship_xy[0] + Ell_rot[0, :], own_ship_xy[1] + Ell_rot[1, :]]
    return domain_path


def goodwindomain(own_ship_xy, cog):
    """
    Parameters
    ----------
    own_ship_xy : (float, float)
        xy coordinates of ellipse centre.
    cog : scalar, optional
        Rotation in degrees anti-clockwise.
    """
    thita = np.array([cog, cog + 112.5, cog + 247.5, cog + 360])
    # number_of_scetor:
    #   use the number_of_scetor to control the result of sector.
    #   defalut values is 100, that means every sector have 100 points.
    #   sector_tem: (x,y), size:(2, number_of_scetor)
    number_of_scetor = 100
    radius_domain =[1.852*1000*x for x in [0.85, 0.4, 0.7]]
    thita_deg = pi * thita / 180
    sector = np.zeros(shape=(2, 3 * number_of_scetor + 1))
    # calculate the sectors
    num_start = 0
    for jj in range(0, thita_deg.shape[0] - 1):
        print(num_start)
        t = np.linspace(thita_deg[jj], thita_deg[jj + 1], number_of_scetor)
        sector_tem = np.array([radius_domain[jj] * np.sin(t), radius_domain[jj] * np.cos(t)])
        sector[:, num_start:num_start + number_of_scetor] = sector_tem[:, :]
        num_start = num_start + number_of_scetor
    sector[:, 3 * number_of_scetor] = sector[:, 0]
    sector[0, :] += own_ship_xy[0]
    sector[1, :] += own_ship_xy[1]
    ship_sector = sector.copy()
    return ship_sector

def ship_shap_base(length, width):
    #ship_path = [[0, length/2], [width/2, length/10], [width/2, -length/2],
    #             [-width/2, -length/2], [width/2, -length/10], [0, length/2]]
    tem_ship = [(0, length / 2), (width / 2, length / 10), (width / 2, -length / 2),
                 (-width / 2, -length / 2), (-width / 2, length / 10), (0, length / 2)]
    ship_path = np.array(tem_ship, float)
    return ship_path

def ship_shape(ship_path, cog):
    t_rot = pi * cog / 180
    R_rot = np.array([[cos(t_rot), sin(t_rot)], [-sin(t_rot), cos(t_rot)]])
    ship_rot = np.zeros((2, ship_path.shape[1]))
    for i in range(ship_path.shape[1]):
        ship_rot[:, i] = np.dot(R_rot, ship_path[:, i])
    return ship_rot.T


if __name__ == '__main__':
    # - ship infomation
    length = 120.0
    width = 30.0
    ownship_x = 100.0
    ownship_y = 0.5
    cog = 0
    # - process
    ship_path_base = ship_shap_base(length, width)
    ship_path = ship_shape(ship_path_base.T, cog)
    # move the center of ship to real position
    ship_ver = ship_path.copy()
    ship_ver[:, 1] = ship_path[:, 1] + ownship_y
    ship_ver[:, 0] = ship_path[:, 0] + ownship_x
    # calculate the domain
    domain_ship = fujidomain((ownship_x, ownship_y), length, cog)
    domain_ship_g = goodwindomain((ownship_x, ownship_y), cog)

    # ----------------------------#
    #  plot the ship domain
    # ----------------------------#
    path = Path(ship_ver)
    pathpatch = PathPatch(path, facecolor='gray', edgecolor='k')
    #
    fig, ax = plt.subplots()
    ax.add_patch(pathpatch)
    plt.plot(domain_ship[0], domain_ship[1], 'gray' )    # rotated ellipse
    plt.plot(domain_ship_g[0], domain_ship_g[1], 'blue' )    # rotated ellipse
    plt.grid(color='lightgray', linestyle='--')
    ax.set_aspect(1.0)
    plt.show()
