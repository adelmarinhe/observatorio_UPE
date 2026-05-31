title_font_size = 18
font_size = 16

def config_layout(figure):
    figure.update_layout(
        legend_title_font_size=title_font_size,
        legend_font_size=font_size,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        modebar=dict(
            bgcolor="rgba(0,0,0,0)",
            color="gray",
            activecolor="white"
            )
    )

    figure.update_xaxes(
    title_font_size=title_font_size,        # Tamanho do título do eixo X
    tickfont_size=font_size                 # Tamanho dos dados do eixo X
    )

    figure.update_yaxes(
        title_font_size=title_font_size,    # Tamanho do título do eixo Y
        tickfont_size=font_size             # Tamanho dos dados do eixo Y
    )