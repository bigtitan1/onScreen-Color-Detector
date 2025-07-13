def _get_color_name(self, rgb):
        try:
            return webcolors.rgb_to_name(rgb)
        except ValueError:
            min_distance = float('inf')
            closest_name = "Unknown"
            for name in webcolors.names("css3"):
                hex_code = webcolors.name_to_hex(name)
                r_c, g_c, b_c = webcolors.hex_to_rgb(hex_code)
                dist = (r_c - rgb[0])**2 + (g_c - rgb[1])**2 + (b_c - rgb[2])**2
                if dist < min_distance:
                    min_distance = dist
                    closest_name = name
            return closest_name