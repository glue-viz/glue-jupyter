<template>
    <div>
        <div>
            <v-select :items="reference_data_items" label="reference" v-model="reference_data_selected" hide-details/>
        </div>
        <div>
            <v-select :items="x_att_items" label="x axis" v-model="x_att_selected" hide-details/>
        </div>
        <div>
            <v-select :items="x_display_unit_items" label="x axis units" v-model="x_display_unit_selected" hide-details/>
        </div>
        <div>
            <v-select :items="y_display_unit_items" label="y axis units" v-model="y_display_unit_selected" hide-details/>
        </div>
        <div>
            <v-select :items="function_items" label="function" v-model="function_selected"/>
        </div>

        <div class="d-inline-flex flex-wrap">
            <v-btn-toggle dense multiple :value="modeSet" @change="modeSetChange" style="margin-right: 8px">

                <v-tooltip bottom>
                    <template v-slot:activator="{ on }">
                        <v-btn v-on="on" small value="normalize">
                            <v-icon>unfold_more</v-icon>
                        </v-btn>
                    </template>
                    <span>normalize</span>
                </v-tooltip>

            </v-btn-toggle>

            <v-switch v-model="glue_state.show_axes" label="Show axes" hide-details style="margin-top: 0"/>
        </div>
    </div>
</template>

<script>
    module.exports = {
        computed: {
            modeSet() {
                return [this.glue_state.normalize && 'normalize']
            }
        },
        methods: {
            modeSetChange(v) {
                this.glue_state.normalize = v.includes('normalize');
            }
        }
    }
</script>

<style id="viewer_profile">
    .v-input--switch label.v-label {
        white-space: nowrap;
    }
</style>
