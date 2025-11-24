<template>
  <div>
        <v-row dense>
          <v-col cols="6">
            <v-text-field label="xmin" v-model="value.x_min"/>
          </v-col>

          <v-col cols="6">
            <v-text-field label="xmax" v-model="value.x_max"/>
          </v-col>
        </v-row>

        <v-row dense>
          <v-col cols="6">
            <v-text-field label="ymin" v-model="value.y_min"/>
          </v-col>

          <v-col cols="6">
            <v-text-field label="ymax" v-model="value.y_max"/>
          </v-col>
        </v-row>
        <div>
          <v-row dense>
            <v-text-field label="x-label" v-model="value.x_axislabel"/>
          </v-row>
          <v-row dense>
            <v-text-field label="y-label" v-model="value.y_axislabel"/>
          </v-row>
        </div>
        <div>
          <v-subheader class="pl-0 slider-label">x tick size</v-subheader>
          <glue-throttled-slider wait="300" min="1" max="20" step="0.01" :value.sync="value.x_ticklabel_size" hide-details />
        </div>
        <div>
          <v-subheader class="pl-0 slider-label">y tick size</v-subheader>
          <glue-throttled-slider wait="300" min="1" max="20" step="0.01" :value.sync="value.y_ticklabel_size" hide-details />
        </div>
  </div>
</template>

<script>
    /* `glue_state` is linked to the text-field and `value` will only be updated when it's a valid number
       This means that any formatting such as '1e3' will be kept.
       Only when `value` is changed externally, `glue_state` will be update according to the current `value`.
    */
    module.exports = {
        props: { value: { type: Object, default: () => ({ x_min: 0, x_max: 1, y_min: 0, y_max: 1}) } },
    }
</script>
