<template>
  <div class="glue-layer-volume-3d">
    <div>
      <v-subheader class="pl-0">lighting</v-subheader>
      <v-switch v-model="lighting" hide-details style="margin-top: 0" />
    </div>
    <div>
      <v-select label="Render method" :items="render_method_items" v-model="render_method_selected" hide-details />
    </div>
    <div>
      <glue-float-field label="vmin" :value.sync="vmin" echo-type="float" />
      <glue-float-field label="vmax" :value.sync="vmax" echo-type="float" />
    </div>
    <div>
      <v-subheader class="pl-0">clamp minimum</v-subheader>
      <v-switch v-model="clamp_min" hide-details style="margin-top: 0" />
    </div>
    <div>
      <v-subheader class="pl-0">clamp maximum</v-subheader>
      <v-switch v-model="clamp_max" hide-details style="margin-top: 0" />
    </div>
    <template v-if="!is_subset">
      <div class="text-subtitle-2 font-weight-bold">Color</div>
      <div>
          <v-select label="color" :items="color_mode_items" v-model="color_mode_selected" hide-details />
      </div>
      <template v-if="(color_mode_items[color_mode_selected] || {}).text === 'Linear'">
        <div>
            <glue-float-field label="min" :value.sync="vmin" echo-type="float" />
        </div>
        <div>
            <glue-float-field label="max" :value.sync="vmax" echo-type="float" />
        </div>
        <div>
            <v-select label="colormap" :items="cmap_items" v-model="cmap" hide-details />
        </div>
      </template>
    </template>
    <div>
      <v-slider label="Opacity" v-model="alpha" :min="0" :max="1" :step="0.001" hide-details />
    </div>
    <div>
      <v-slider label="Opacity scale" v-model="opacity_scale" :min="-3" :max="3" :step="0.01" hide-details />
    </div>
    <div>
      <v-select label="Stretch" :items="stretch_items" v-model="stretch_selected" hide-details />
    </div>
    </div>
  </div>
</template>

<style id="layer_volume">
    .v-subheader {
        font-size: 12px;
        height: 16px;
    }
</style>
