<template>
    <div>
        <div>
            <v-select :items="x_att_items" label="x axis" v-model="x_att_selected"/>
        </div>
        <div>
            <v-btn-toggle dense multiple :value="modeSet" @change="modeSetChange">

                <v-tooltip bottom>
                    <template v-slot:activator="{ on }">
                        <v-btn v-on="on" small value="normalize">
                            <v-icon>unfold_more</v-icon>
                        </v-btn>
                    </template>
                    <span>normalize</span>
                </v-tooltip>

                <v-tooltip bottom>
                    <template v-slot:activator="{ on }">
                        <v-btn v-on="on" small value="cumulative">
                            <v-icon>trending_up</v-icon>
                        </v-btn>
                    </template>
                    <span>cumulative</span>
                </v-tooltip>
            </v-btn-toggle>
        </div>

        <v-switch v-model="glue_state.show_axes" label="Show axes" hide-details/>
    </div>
</template>
<script>
    module.exports = {
        computed: {
            modeSet() {
                return [this.glue_state.normalize && 'normalize', this.glue_state.cumulative && 'cumulative']
            }
        },
        methods: {
            modeSetChange(v) {
                this.glue_state.normalize = v.includes('normalize');
                this.glue_state.cumulative = v.includes('cumulative');
            }
        }
    }
</script>
