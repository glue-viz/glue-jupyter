<template>
  <v-container class="pa-4" max-width="1080">
    <v-card class="pa-4">
      <v-card-title>Set Figure Bounds</v-card-title>
      <v-card-text>
        <v-row dense>
          <v-col cols="3">
            <v-text-field v-model="xmin" label="X Min" type="number" outlined />
          </v-col>

          <v-col cols="3">
            <v-text-field v-model="xmax" label="X Max" type="number" outlined />
          </v-col>
        </v-row>
        <v-row dense>
          <v-col cols="3">
            <v-text-field v-model="ymin" label="Y Min" type="number" outlined />
          </v-col>

          <v-col cols="3">
            <v-text-field v-model="ymax" label="Y Max" type="number" outlined />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>
