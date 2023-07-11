<template>
    <div>
        <div class="text-subtitle-2 mt-4 mb-2 font-weight-bold">Color</div>
        <div>
            <v-select label="color" :items="cmap_mode_items" v-model="cmap_mode_selected" hide-details />
        </div>
        <div v-if="glue_state.cmap_mode === 'Linear'">
            <v-select label="attribute" :items="cmap_att_items" v-model="cmap_att_selected" hide-details
                class="margin-bottom: 16px" />
        </div>
        <div v-if="glue_state.cmap_mode === 'Linear'">
            <v-text-field label="min" v-model="glue_state.cmap_vmin" hide-details
                class="margin-bottom: 16px"></v-text-field>
        </div>
        <div v-if="glue_state.cmap_mode === 'Linear'">
            <v-text-field label="max" v-model="glue_state.cmap_vmax" hide-details
                class="margin-bottom: 16px"></v-text-field>
        </div>
        <div v-if="glue_state.cmap_mode === 'Linear'">
            <v-select label="colormap" :items="cmap_items" :value="glue_state.cmap" @change="set_colormap" hide-details
                class="margin-bottom: 16px" />
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">opacity</v-subheader>
            <glue-throttled-slider wait="300" min="0" max="1" step="0.01" :value.sync="glue_state.alpha" hide-details />
        </div>
        <div class="text-subtitle-2 mt-4 mb-2 font-weight-bold">Points</div>
        <div>
            <v-subheader class="pl-0 slider-label">show points</v-subheader>
            <v-switch v-model="glue_state.markers_visible" hide-details style="margin-top: 0" />
        </div>
        <div v-if="glue_state.markers_visible">
            <v-select label="type" :items="points_mode_items" v-model="points_mode_selected" hide-details />
        </div>
        <div v-if="glue_state.markers_visible && glue_state.density_map === false">
            <v-select label="size" :items="size_mode_items" v-model="size_mode_selected" hide-details />
        </div>
        <div v-if="glue_state.markers_visible && glue_state.size_mode === 'Linear'">
            <v-select label="attribute" :items="size_att_items" v-model="size_att_selected" hide-details
                class="margin-bottom: 16px" />
        </div>
        <div v-if="glue_state.markers_visible && glue_state.size_mode === 'Linear'">
            <v-text-field label="min" v-model="glue_state.size_vmin" hide-details
                class="margin-bottom: 16px"></v-text-field>
        </div>
        <div v-if="glue_state.markers_visible && glue_state.size_mode === 'Linear'">
            <v-text-field label="max" v-model="glue_state.size_vmax" hide-details
                class="margin-bottom: 16px"></v-text-field>
        </div>
        <div v-if="glue_state.markers_visible && !glue_state.density_map">
            <v-subheader class="pl-0 slider-label">fill markers</v-subheader>
            <v-switch v-model="glue_state.fill" hide-details style="margin-top: 0" />
        </div>
        <div v-if="glue_state.markers_visible && !glue_state.density_map">
            <v-subheader class="pl-0 slider-label">size scaling</v-subheader>
            <glue-throttled-slider wait="300" min="0.1" max="10" step="0.01" :value.sync="glue_state.size_scaling"
                hide-details />
        </div>
        <div v-if="glue_state.markers_visible && glue_state.density_map">
            <v-subheader class="pl-0 slider-label">dpi</v-subheader>
            <glue-throttled-slider wait="300" min="12" max="144" step="1" :value.sync="dpi" hide-details />
        </div>
        <div v-if="glue_state.markers_visible && glue_state.density_map">
            <v-subheader class="pl-0 slider-label">contrast</v-subheader>
            <glue-throttled-slider wait="300" min="0" max="1" step="0.01" :value.sync="glue_state.density_contrast"
                hide-details />
        </div>
        <div class="text-subtitle-2 mt-4 mb-2 font-weight-bold">Vectors</div>
        <div>
            <v-subheader class="pl-0 slider-label">show vectors</v-subheader>
            <v-switch v-model="glue_state.vector_visible" hide-details />
        </div>
        <div v-if="glue_state.vector_visible">
            <v-select label="vx" :items="vx_att_items" v-model="vx_att_selected" hide-details />
        </div>
        <div v-if="glue_state.vector_visible">
            <v-select label="vy" :items="vy_att_items" v-model="vy_att_selected" hide-details style="margin-bottom: 16px" />
        </div>
    </div>
</template>
<script>
</script>
<style id="layer_scatter">
.v-subheader.slider-label {
    font-size: 12px;
    height: 16px;
}
</style>
