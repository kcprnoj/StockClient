style = dict(style_name    = 'nightclouds',
             base_mpl_style='dark_background', 
             marketcolors  = {'candle'  : {'up':'w', 'down':'#0095ff'},
                              'edge'    : {'up':'w', 'down':'#0095ff'},
                              'wick'    : {'up':'w', 'down':'w'},
                              'ohlc'    : {'up':'w', 'down':'w'},
                              'volume'  : {'up':'w', 'down':'#0095ff'},
                              'vcdopcod': False,
                              'alpha'   : 1.0,
                             },
             mavcolors     = ['#40e0d0','#ff00ff','#ffd700','#1f77b4',
                              '#ff7f0e','#2ca02c','#e377c2'],
             y_on_right    = False,
             facecolor     = '#1A232D',
             gridcolor     = '#999999',
             gridstyle     = '--',
             rc            = [('patch.linewidth' ,  1.0      ),
                              ('lines.linewidth' ,  1.0      ),
                              ('figure.titlesize', 'x-large' ),
                              ('figure.titleweight','semibold'),
                              ('figure.facecolor', '#1A232D'),
                              ('font.size', 9.0)
                             ],
             base_mpf_style='nightclouds', 
            )
