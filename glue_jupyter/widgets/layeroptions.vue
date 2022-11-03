<template>
    <div class="glue-layer-options">
        <div>
            <v-select
                    :items="layers"
                    item-text="label"
                    item-value="index"
                    v-model="selected"
                    label="Layer"
                    hide-details
            >
                <template slot="selection" slot-scope="data">
                    <div class="single-line">
                        <v-menu v-model="color_menu_open">
                            <template v-slot:activator="{ on }">
                                <span class="glue-color-menu"
                                      :style="`background:${data.item.color}`"
                                      @click.stop="on.click"
                                >&nbsp;</span>
                            </template>
                            <div @click.stop="" style="text-align: end; background-color: white">
                                <v-btn icon @click="color_menu_open = false">
                                    <v-icon>mdi-close</v-icon>
                                </v-btn>
                                <v-color-picker v-model="data.item.color"></v-color-picker>
                            </div>
                        </v-menu>
                        <v-btn icon @click.stop="data.item.visible = !data.item.visible">
                            <v-icon>mdi-eye{{ data.item.visible ? '' : '-off' }}</v-icon>
                        </v-btn>
                        {{ data.item.label }}
                    </div>
                </template>
                <template slot="item" slot-scope="data">
                    <div class="single-line">
                        <span class="glue-color-menu"
                              :style="`background:${data.item.color}`"
                        >&nbsp;</span>
                        <v-icon style="padding: 0 4px" @click.stop="data.item.visible = !data.item.visible">
                            mdi-eye{{ data.item.visible ? '' : '-off' }}
                        </v-icon>
                        {{ data.item.label }}
                    </div>
                </template>
            </v-select>
        </div>
        <div>
            <jupyter-widget v-if="layers && current_panel" :widget="current_panel"></jupyter-widget>
        </div>
    </div>
</template>

<style id="glue-layeroptions">
    .glue-layer-options {
        width: 100%;
    }

    .glue-color-menu {
        font-size: 16px;
        padding-left: 16px;
        border: 2px solid rgba(0,0,0,0.54);
    }

    .single-line {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        width: 100%;
    }
</style>
