<template>
    <div class="glue-viewer-image">
        <div>
            <v-select label="mode" :items="color_mode_items" v-model="color_mode_selected" hide-details />
        </div>
        <div>
            <v-select label="reference" :items="reference_data_items" v-model="reference_data_selected" hide-details />
        </div>
        <div class="glue-viewer-image-switches">
            <div>
                <v-subheader class="pl-0 slider-label">equal aspect ratio</v-subheader>
                <v-switch input-value="glue_state.aspect === EQUAL" @change="setEqualAspect" hide-details style="margin-top: 0" />
            </div>
            <div>
                <v-subheader class="pl-0 slider-label">show axes</v-subheader>
                <v-switch v-model="glue_state.show_axes" hide-details style="margin-top: 0"/>
            </div>
        </div>
        <div>
            <v-select label="x axis" :items="x_att_world_items" v-model="x_att_world_selected" hide-details />
        </div>
        <div>
            <v-select label="y axis" :items="y_att_world_items" v-model="y_att_world_selected" hide-details style="margin-bottom: 16px" />
        </div>
        <div v-for="slider of sliders">
            <v-subheader class="pl-0 slider-label">{{ slider.label }}: {{ glue_state.slices[slider.index] }} ({{  slider.world_value  }} {{ slider.unit }})</v-subheader>
            <glue-throttled-slider
                v-if="glue_state.slices && glue_state.slices.length > 0"
                wait="300" :max="slider.max" :value.sync="glue_state.slices[slider.index]" hide-details />
        </div>
    </div>
</template>
<script>
    modules.export = {
        created() {
            this.EQUAL = 'equal';
            this.AUTO = 'auto';
        },
        methods: {
            setEqualAspect(value) {
                this.glue_state.aspect = value ? this.EQUAL : this.AUTO;
            },
        }
    }
</script>
<style id="viewer_image">
    .glue-viewer-image {
        width: 100%;
    }

    .glue-viewer-image-switches {
        display: flex;
        flex-direction: row;
    }

    .v-subheader.slider-label {
        font-size: 12px;
        height: 16px;
    }
</style>
