<template>
    <div class="glue-viewer-scatter">
        <div>
            <v-select label="x axis" :items="x_att_items" v-model="x_att_selected" hide-details />
        </div>
        <div>
            <v-select label="y axis" :items="y_att_items" v-model="y_att_selected" hide-details />
        </div>
        <div>
            <v-select :items="x_display_unit_items" label="x axis units" v-model="x_display_unit_selected" hide-details/>
        </div>
        <div>
            <v-select :items="y_display_unit_items" label="y axis units" v-model="y_display_unit_selected" hide-details/>
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">show axes</v-subheader>
            <v-switch v-model="glue_state.show_axes" hide-details style="margin-top: 0"/>
        </div>
    </div>
</template>

<style id="viewer_image">
    .glue-viewer-scatter .v-subheader.slider-label {
        font-size: 12px;
        height: 16px;
        margin-top: 6px;
    }
</style>
