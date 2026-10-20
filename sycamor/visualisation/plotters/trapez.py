from matplotlib import pyplot as plt
from datetime import datetime

import numpy as np

from sycamor.ca.classification.scheme import TrapezoidalDefinition
from sycamor.ca.region_growing.main import alpha_quadratic_function
from sycamor.config.syCAMOR import ALPHA, TIME_MAX
from sycamor.visualisation.plot import addStyle

addStyle()
def plotTrapRaw(trap: TrapezoidalDefinition, ptsY):
    ptsX  = trap.getDimensions()
    
    
    
    
    letterLabels = ['a', 'b', 'c', 'd']
    fig, ax = plt.subplots( )
    
    ax.set_xticks(ptsX, letterLabels)
    ylim = ( 0, 1.5)
    xlim =( 0, 5)
    ax.set_ylim(ylim)
    ax.set_xlim(xlim)
    ax.set_yticks([1])
        
    ax.hlines(y=1, xmin=0, xmax=trap.b, color='gray', linestyle='--')
    ax.vlines(x=trap.b, ymin=0, ymax=1, color='gray', linestyle='--')
    ax.vlines(x=trap.c, ymin=0, ymax=1, color='gray', linestyle='--')
    ax.set_frame_on(False) 
    
       
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')

    # Hide the top and right spines (borders)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add arrowheads to the axes using annotate
    ax.annotate(
        '',
        xy=(1.05, 0),
        xycoords=('axes fraction', 'data'),
        xytext=(-0.05, 0),
        textcoords=('axes fraction', 'data'),
        arrowprops=dict(arrowstyle='->', ec='black', lw=1),
    )
    ax.annotate(
        '',
        xy=(0, 1.05),
        xycoords=('data', 'axes fraction'),
        xytext=(0, -0.05),
        textcoords=('data', 'axes fraction'),
        arrowprops=dict(arrowstyle='->', ec='black', lw=1),
    )
    
    # 5. Add custom 'x' and 'y' labels positioned near the arrowheads
    ax.text(max(xlim), 0.05, "x", fontsize=12, ha="right", va="bottom")
    ax.text(0.1, max(ylim), "y", fontsize=12, ha="left", va="top")

    # Show the clean plot
    plt.grid(True, linestyle="--", alpha=0.5)
    
    ax.set_aspect('equal', adjustable='box')

    ax.plot(ptsX, ptsY, color="black")
    plt.savefig('results/membership/trapezoid_' + datetime.now().strftime("%Y%m%d_%H%M%S")+".png", dpi=300, bbox_inches='tight')
   
    plt.show()
    
def plotTrap():
    addStyle()
    ptsY = [0, 1, 1, 0]
    plotTrapRaw(TrapezoidalDefinition(1,2,3,4), ptsY)

def plotAlpha():
    xlim = (0,TIME_MAX+100)
    ylim = (0,1)

    # 2. Generate 400 evenly spaced points between -5 and 5
    x_values = np.linspace(0, TIME_MAX+1, 400)

    # 3. Calculate corresponding y values
    y_values = alpha_quadratic_function(x_values)
    y_mEMvalues = np.ones_like(x_values)-alpha_quadratic_function(x_values) 
  
    fig, ax = plt.subplots( )
    
    x_ticks = np.arange(0, TIME_MAX, 100)
    y_ticks = np.arange(0, 1.1, 0.1)
    ylim = ( 0, 1)
    xlim =( 0, TIME_MAX)
    ax.set_ylim(ylim)
    ax.set_xlim(xlim)
    ax.set_yticks(y_ticks)
    ax.set_xticks(x_ticks)
    
    ax.tick_params(axis='y', colors='black')
    ax.tick_params(axis='x', colors='black')
    
    ax.set_xlabel("Time Step, t")
    ax.set_ylabel("Proportion of Contribution")
        
    ax.set_frame_on(False) 
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')

    # Hide the top and right spines (borders)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add arrowheads to the axes using annotate
    ax.annotate(
        '',
        xy=(1.05, 0),
        xycoords=('axes fraction', 'data'),
        xytext=(-0.05, 0),
        textcoords=('axes fraction', 'data'),
        arrowprops=dict(arrowstyle='->', ec='black', lw=1),
    )
    ax.annotate(
        '',
        xy=(0, 1.05),
        xycoords=('data', 'axes fraction'),
        xytext=(0, -0.05),
        textcoords=('data', 'axes fraction'),
        arrowprops=dict(arrowstyle='->', ec='black', lw=1),
    )
    categories = ["Radar Membership", "Neighbourhood Membership"]
    ax.text(max(xlim)/4, max(ylim)/4, "Radar\nMembership", fontsize=12, color="black", ha='center',va='center' )
    ax.text(max(xlim)*3/4, max(ylim)*3/4, "Neighbourhood\nMembership", fontsize=12, color="black", ha='center',va='center' )
        
   
    # Show the clean plot
    plt.grid(True, linestyle="--", alpha=0.5)
    
    ax.bar(x_values, y_mEMvalues, label="Radar Membership", color="#9fd096", width=100, align='edge')
    ax.bar(x_values, y_values, bottom=y_mEMvalues, label="Neighbourhood Membership", color="#e4d5ab",  width=100, align='edge')
    
    plt.savefig('results/membership/alpha_' + datetime.now().strftime("%Y%m%d_%H%M%S")+".png", dpi=300, bbox_inches='tight')
    
    plt.show()
if __name__ == '__main__':
    plotAlpha()