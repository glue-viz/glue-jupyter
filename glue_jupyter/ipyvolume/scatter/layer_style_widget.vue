<template>
  <div class="glue-layer-scatter-3d">
    <div>
      <v-subheader class="pl-0">visible</v-subheader>
      <v-switch v-model="visible" hide-details style="margin-top: 0" />
    </div>
    <div>
      <v-select label="Marker" :items="geo_items" v-model="geo_selected" hide-details />
    </div>
    <div>
      <jupyter-widget :widget="widget_size" />
    </div>
    <div>
      <jupyter-widget :widget="widget_color" />
    </div>
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
