<div id="app">
    <v-app id="inspire">
        <div>
            <v-menu :close-on-content-click="!multiple" offset-y>
                <template #activator="{ props }">
                    <div v-bind="props">
                        <v-chip v-if="selected.length === 0">
                            <v-icon start>add</v-icon>
                            No selection (create new)
                        </v-chip>
                        <div v-else>
                            <v-chip v-for="index in selected" :key=index>
                                <v-icon start :color="available[index].color">
                                    signal_cellular_4_bar
                                </v-icon>
                                {{ available[index].label }}
                            </v-chip>
                        </div>
                    </div>
                </template>
                <v-list>
                    <v-list-item>
                        <v-switch v-model="multiple" label="Multiple" @click="handleMultiple"></v-switch>
                    </v-list-item>
                    <v-list-item
                            @click="multiple = false;selected=[]"
                            :class="selected.length === 0 ? 'v-list-item--active' : ''">
                        <template #prepend>
                            <v-icon>add</v-icon>
                        </template>
                        <v-list-item-title>{{ no_selection_text }}</v-list-item-title>

                    </v-list-item>
                    <v-list-item
                            v-for="(item, index) in available"
                            :key="item.label"
                            :class="(selected.includes(index)) ? 'v-list-item--active' : ''"
                            @click="toggleSubset(index)">
                        <template #prepend>
                            <v-icon :color="item.color">signal_cellular_4_bar</v-icon>
                        </template>

                        <v-list-item-title>{{ item.label }}</v-list-item-title>
                    </v-list-item>
                </v-list>
            </v-menu>
        </div>
    </v-app>
</div>
