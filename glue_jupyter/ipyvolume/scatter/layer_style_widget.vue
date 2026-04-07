<template>
  <div class="glue-layer-scatter-3d">
    <div>
      <v-subheader class="pl-0">visible</v-subheader>
      <v-switch v-model="visible" hide-details style="margin-top: 0" />
    </div>
    <div>
      <v-select label="Marker" :items="geo_items" v-model="geo_selected" hide-details />
    </div>
    <div class="text-subtitle-2 font-weight-bold">Size</div>
    <div>
      <v-select label="size" :items="size_mode_items" v-model="size_mode_selected" hide-details />
    </div>
    <template v-if="(size_mode_items[size_mode_selected] || {}).text === 'Linear'">
      <div>
          <v-select label="attribute" :items="size_att_items" v-model="size_att_selected" hide-details />
      </div>
      <div>
          <glue-float-field label="min" :value.sync="size_vmin" echo-type="float" />
      </div>
      <div>
          <glue-float-field label="max" :value.sync="size_vmax" echo-type="float" />
      </div>
      <div>
          <v-subheader class="pl-0 slider-label">size scaling</v-subheader>
          <glue-throttled-slider wait="300" min="0.1" max="10" step="0.01" :value.sync="size_scaling" echo-type="float"
              hide-details />
      </div>
    </template>
    <template v-else>
      <div>
          <glue-float-field label="size" :value.sync="size" echo-type="int" />
      </div>
    </template>
    <div class="text-subtitle-2 font-weight-bold">Color</div>
    <div>
        <v-select label="color" :items="color_mode_items" v-model="color_mode_selected" hide-details />
    </div>
    <template v-if="(color_mode_items[color_mode_selected] || {}).text === 'Linear'">
      <div>
          <v-select label="attribute" :items="cmap_att_items" v-model="cmap_att_selected" hide-details />
      </div>
      <div>
          <glue-float-field label="min" :value.sync="cmap_vmin" echo-type="float" />
      </div>
      <div>
          <glue-float-field label="max" :value.sync="cmap_vmax" echo-type="float" />
      </div>
      <div>
          <v-select label="colormap" :items="cmap_items" v-model="cmap" hide-details />
      </div>
    </template>
    <div>
      <v-subheader class="pl-0">show vectors</v-subheader>
      <v-switch v-model="vector_visible" hide-details style="margin-top: 0" />
      <template v-if="vector_visible">
        <v-select label="vx" :items="vx_att_items" v-model="vx_att_selected" />
        <v-select label="vy" :items="vy_att_items" v-model="vy_att_selected" />
        <v-select label="vz" :items="vz_att_items" v-model="vz_att_selected" />
      </template>
    </div>
  </div>
</template>

<style id="viewer_3d">
    .v-subheader.slider-label {
        font-size: 12px;
        height: 16px;
    }
</style>
