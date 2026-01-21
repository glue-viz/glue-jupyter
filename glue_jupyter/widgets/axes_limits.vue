<template>
  <div>
  <v-row no-gutters>
    <v-col cols="6">
      <glue-float-field class="mr-1" label="xmin" :value.sync="x_min" />
    </v-col>
    <v-col  cols="6">
      <glue-float-field class="ml-1" label="xmax" :value.sync="x_max" />
    </v-col>
  </v-row>
  <v-row no-gutters>
    <v-col cols="6">
      <glue-float-field class="mr-1" label="ymin" :value.sync="y_min" />
    </v-col>
    <v-col cols="6">
      <glue-float-field class="ml-1" label="ymax" :value.sync="y_max" />
    </v-col>
  </v-row>
  <v-row>
    <v-col class="text-center" cols="12">
    <v-btn @click="apply_limits">
      Apply limits
    </v-btn>
    </v-col>
  </v-row>
  </div>
</template>
