<template>
  <div class="glue-viewer-3d">
    <div>
      <v-subheader class="pl-0 slider-label">show axes</v-subheader>
      <v-switch v-model="show_axes" hide-details style="margin-top: 0" />
    </div>
    <div>
      <v-subheader class="pl-0 slider-label">native aspect ratio</v-subheader>
      <v-switch v-model="native_aspect" hide-details style="margin-top: 0" />
    </div>
    <div>
      <v-select label="resolution" :items="resolution_items" v-model="resolution" hide-details />
    </div>
    <div>
      <v-select label="x-axis" :items="x-att_items" v-model="x_att_selected" hide-details />
    </div>
    <div>
      <v-select label="y-axis" :items="y-att_items" v-model="y_att_selected" hide-details />
    </div>
    <div v-if="has_resolution">
      <v-select label="z-axis" :items="z-att_items" v-model="z_att_selected" hide-details />
    </div>
    <div v-if="has_figure"> 
      <v-subheader class="pl-0">show movie maker</v-subheader>
      <v-switch @change="set_movie_maker_visible" hide-details style="margin-top: 0" />
      <jupyter-widget :widget="movie_maker_layout" />
    </div>
  </div>
</template>
