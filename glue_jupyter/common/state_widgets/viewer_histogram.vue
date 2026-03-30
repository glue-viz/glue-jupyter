<template>
    <div>
        <div>
            <v-select :items="x_att_items" label="x axis" v-model="x_att_selected"/>
        </div>
        <div>
            <v-text-field type="number" step="1" label="number of bins" v-model.number="hist_n_bin" />
        </div>
        <div>
            <glue-float-field label="x-min" :value.sync="hist_x_min" echo-type="float" />
        </div>
        <div>
            <glue-float-field label="x-max" :value.sync="hist_x_max" echo-type="float" />
        </div>
        <div>
            <v-switch v-model="normalize" label="Normalize" hide-details/>
        </div>
        <div>
            <v-switch v-model="cumulative" label="Cumulative" hide-details/>
        </div>
        <div>
            <v-btn variant="outlined" size="x-small" @click="bins_to_axis">
                Fit Bins to Axes
            </v-btn>
        </div>
        <v-switch v-model="show_axes" label="Show axes" hide-details/>
    </div>
</template>
