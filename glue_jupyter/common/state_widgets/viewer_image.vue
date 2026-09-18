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
                <div class="slider-label">equal aspect ratio</div>
                <v-switch :model-value="aspect === 'equal'" @update:modelValue="setEqualAspect" hide-details style="margin-top: 0" />
            </div>
            <div>
                <div class="slider-label">show axes</div>
                <v-switch v-model="show_axes" hide-details style="margin-top: 0"/>
            </div>
        </div>
        <div>
            <v-select label="x axis" :items="x_att_world_items" v-model="x_att_world_selected" hide-details />
        </div>
        <div>
            <v-select label="y axis" :items="y_att_world_items" v-model="y_att_world_selected" hide-details style="margin-bottom: 16px" />
        </div>
        <div v-for="slider of sliders">
            <div class="slider-label">{{ slider.label }}: {{ slices[slider.index] }} ({{  slider.world_value  }} {{ slider.unit }})</div>
            <glue-throttled-slider
                v-if="slices && slices.length > 0"
                wait="300" :max="slider.max" :value="slices[slider.index]" @update:value="updateSlice(slider.index, $event)" hide-details />
        </div>
    </div>
</template>
<script>
    modules.export = {
        methods: {
            setEqualAspect(value) {
                this.aspect = value ? 'equal' : 'auto';
            },
            updateSlice(index, value) {
                var newSlices = this.slices.slice();
                newSlices[index] = value;
                this.slices = newSlices;
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

    .slider-label {
        font-size: 12px;
        height: 16px;
    }
</style>
