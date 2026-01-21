import ipyvue
import ipyvuetify as v
import traitlets
import ipywidgets as widgets
from traitlets import Unicode, Dict, List
import ipywidgets as w

class Disconnect(v.VuetifyTemplate):
    main = traitlets.Instance(widgets.Widget).tag(sync=True, **widgets.widget_serialization)
    broken = traitlets.Instance(widgets.Widget).tag(sync=True, **widgets.widget_serialization)
    connected = traitlets.Bool(True).tag(sync=True)
    template = Unicode("""
    <template>
        <view-context-wrapper :widget="connected ? main : broken"></view-context-wrapper>
    </template>
    """).tag(sync=True)
    
    # we need to put our code in a component, otherwise inject: ['viewCtx'] does not work
    components = Dict({
        'view-context-wrapper': """
            <template>
                <jupyter-widget :widget="widget"></jupyter-widget>
            </template>
            <script>
            module.exports = {
                props: ["widget"],
                inject: ['viewCtx'],
                created() {
                    const model = this.viewCtx.getView().model;
                    model.set('connected', Boolean(model.comm_live));
                    model.on('comm_live_update', () => {
                        const connected = Boolean(model.comm_live)
                        model.set('connected', connected);
                        model.save_changes()
                    })
                },
            };
            </script>
        """
    }).tag(sync=True)
