<template>
    <div class="glue-viewer-histogram">
        <div>
            <v-select :items="x_att_items" label="x axis" v-model="x_att_selected"/>
        </div>
        <div>
            <v-text-field type="number" step="1" label="number of bins" v-model.number="hist_n_bin" />
        </div>
        <div>
            <glue-float-field label="x-min" v-model:value="hist_x_min" echo-type="float" />
        </div>
        <div>
            <glue-float-field label="x-max" v-model:value="hist_x_max" echo-type="float" />
        </div>
        <div>
            <v-switch v-model="normalize" label="Normalize" hide-details/>
        </div>
        <div>
            <v-switch v-model="cumulative" label="Cumulative" hide-details/>
        </div>
        <div>
            <div class="slider-label">log x axis</div>
            <v-switch v-model="x_log" hide-details style="margin-top: 0"/>
        </div>
        <div>
            <div class="slider-label">log y axis</div>
            <v-switch v-model="y_log" hide-details style="margin-top: 0"/>
        </div>
        <div>
            <v-btn variant="outlined" size="x-small" @click="bins_to_axis">
                Fit Bins to Axes
            </v-btn>
        </div>
        <v-switch v-model="show_axes" label="Show axes" hide-details/>
    </div>
</template>

<style id="viewer_histogram">
    .glue-viewer-histogram .slider-label {
        font-size: 12px;
        height: 16px;
        margin-top: 6px;
    }
</style>
