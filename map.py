import pandas as pd
import folium
import math

# =============================================
# إحداثيات المحافظات السورية
# =============================================
province_coords = {
    "Homs":          (34.7324, 36.7137),
    "Aleppo":        (36.2021, 37.1343),
    "Idleb":         (35.9306, 36.6339),
    "Damascus":      (33.5138, 36.2765),
    "Lattakia":      (35.5317, 35.7915),
    "Raqqa":         (35.9500, 39.0100),
    "Hama":          (35.1318, 36.7580),
    "Daraa":         (32.6189, 36.1021),
    "Rural Damascus":(33.4200, 36.5500),
}

# =============================================
# دالة توزيع النقاط بشكل دائري
# =============================================
def spread_points(lat, lon, total, index, radius=0.08):
    if total == 1:
        return lat, lon
    angle = (2 * math.pi / total) * index
    new_lat = lat + radius * math.cos(angle)
    new_lon = lon + radius * math.sin(angle)
    return new_lat, new_lon

# =============================================
# تحميل البيانات
# =============================================
FILE_PATH = r"DSC_list.xlsx"

df_sfr = pd.read_excel(FILE_PATH, sheet_name="SFRs")
df_dsc = pd.read_excel(FILE_PATH, sheet_name="DSCs")

df_sfr.columns = df_sfr.columns.str.strip()
df_dsc.columns = df_dsc.columns.str.strip()
df_sfr["Province"] = df_sfr["Province"].astype(str).str.strip()
df_dsc["Province"] = df_dsc["Province"].astype(str).str.strip()

# =============================================
# حساب العدد الكلي لكل محافظة (DSC + SFR معاً)
# =============================================
all_provinces = pd.concat([df_sfr["Province"], df_dsc["Province"]])
province_counts = all_provinces.value_counts().to_dict()
province_index = {p: 0 for p in province_counts}

# =============================================
# إنشاء الخريطة
# =============================================
m = folium.Map(
    location=[34.8021, 38.9968],
    zoom_start=6,
    tiles="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
    attr="CartoDB",
    min_zoom=5,
    max_zoom=10
)

# تحديد حدود العرض لسوريا فقط
m.fit_bounds([[32.3, 35.7], [37.3, 42.4]])

# --- SFR: أزرق ---
sfr_group = folium.FeatureGroup(name="SFRs (Blue)", show=True)
for _, row in df_sfr.iterrows():
    province = row["Province"]
    if province in province_coords:
        lat, lon = province_coords[province]
        total = province_counts[province]
        idx = province_index[province]
        new_lat, new_lon = spread_points(lat, lon, total, idx)
        province_index[province] += 1

        folium.CircleMarker(
            location=[new_lat, new_lon],
            radius=10,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.8,
            popup=folium.Popup(
                f"<b>{row['Code']}</b><br>{row['Organization']}<br>{province}",
                max_width=200
            ),
            tooltip=str(row["Code"])
        ).add_to(sfr_group)
sfr_group.add_to(m)

# --- DSC: أحمر ---
dsc_group = folium.FeatureGroup(name="DSCs (Red)")
for _, row in df_dsc.iterrows():
    province = row["Province"]
    if province in province_coords:
        lat, lon = province_coords[province]
        total = province_counts[province]
        idx = province_index[province]
        new_lat, new_lon = spread_points(lat, lon, total, idx)
        province_index[province] += 1

        folium.CircleMarker(
            location=[new_lat, new_lon],
            radius=10,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.8,
            popup=folium.Popup(
                f"<b>{row['Code']}</b><br>{row['Organization']}<br>{province}",
                max_width=200
            ),
            tooltip=str(row["Code"])
        ).add_to(dsc_group)
dsc_group.add_to(m)

# =============================================
# حفظ الخريطة
# =============================================
folium.LayerControl().add_to(m)
OUTPUT = "map_output.html"
m.save(OUTPUT)
print(f"✅ الخريطة محفوظة: {OUTPUT}")
print("افتح map_output.html بالمتصفح.")