<template>
    <div>
        <div>
            <v-select label="attribute" :items="attribute_items" v-model="attribute_selected" hide-details class="margin-bottom: 16px" />
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">opacity</v-subheader>
            <v-slider max="1" step="0.01" :value="glue_state.alpha" @end="setAlpha" hide-details />
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">contrast</v-subheader>
            <v-slider max="4" step="0.01" :value="glue_state.contrast" @end="setContrast" hide-details />
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">bias</v-subheader>
            <v-slider max="1" step="0.01" :value="glue_state.bias" @end="setBias" hide-details />
        </div>
        <div>
            <v-select label="stretch" :items="stretch_items" v-model="stretch_selected" hide-details />
        </div>
        <div>
            <v-select label="percentile" :items="percentile_items" v-model="percentile_selected" hide-details />
        </div>
        <div>
            <v-text-field label="min" v-model.number="glue_state.v_min" type="number" hide-details />
        </div>
        <div>
            <v-text-field label="max" v-model.number="glue_state.v_max" type="number" hide-details />
        </div>
        <div v-if="color_mode === 'Colormaps'">
            <v-select label="colormap" :items="colormap_items" :value="glue_state.cmap" @change="set_colormap" />
        </div>
    </div>
</template>
<script>
    modules.export = {
        methods: {
            /* TODO: use @change with debounce instead of @end */
            setAlpha(value) {
                this.glue_state.alpha = value;
            },
            setContrast(value) {
                this.glue_state.contrast = value;
            },
            setBias(value) {
                this.glue_state.bias = value;
            },
        },
    }
</script>
<style id="layer_image">
    .vuetify-styles .v-subheader.slider-label {
        font-size: 12px;
        height: 16px;
    }
</style>
