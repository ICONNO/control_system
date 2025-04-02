import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Introducción',
      items: ['intro'],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Control System',
      items: ['control-system/control_system_overview'],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'GUI',
      items: [
        'control-system/gui/gui_architecture',
        'control-system/gui/serial-communication',
        'control-system/gui/styles'
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Actuador Lineal',
      items: [
        'control-system/gui/linear-actuator/la_overview',
        'control-system/gui/linear-actuator/la_logic',
        'control-system/gui/linear-actuator/la_motor',
        'control-system/gui/linear-actuator/la_sensor'
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Hardware',
      items: ['control-system/hardware'],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Desarrollo',
      items: ['development/development_setup'],
      collapsed: false,
    },
  ],
};

export default sidebars;
