import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'System Control',
  tagline: 'Documentación del código y arquitectura',
  favicon: 'img/favicon.ico',

  // URL de producción (ajústala según sea necesario)
  url: 'https://your-docusaurus-site.example.com',
  baseUrl: '/',

  // Configuración para GitHub Pages (ajústala según corresponda)
  organizationName: 'TuOrganizacion', // Ejemplo: tu usuario u organización
  projectName: 'system-control',       // Nombre de tu repositorio

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          // Configuramos la documentación como homepage
          routeBasePath: '/', 
          sidebarPath: require.resolve('./sidebars.ts'),
          editUrl:
            'https://github.com/TuOrganizacion/system-control/edit/main/docs/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          editUrl:
            'https://github.com/TuOrganizacion/system-control/edit/main/docs/',
        },
        // Si deseas conservar el blog, déjalo; si no, cámbialo a false.
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',
    navbar: {
      // Puedes dejar el título vacío para no mostrar "My Site"
      title: '',
      logo: {
        alt: 'System Control Logo',
        src: 'img/logo.svg',
        href:'/intro',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Documentation',
        },
        // Eliminamos el enlace al blog (opcional)
        {
          href: 'https://github.com/ICONNO/control_system',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Documentation',
              to: '/docs/intro', // Asegúrate de que el ID del doc de introducción sea "intro" o ajusta aquí
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'Stack Overflow',
              href: 'https://stackoverflow.com/questions/tagged/docusaurus',
            },
            {
              label: 'Discord',
              href: 'https://discordapp.com/invite/docusaurus',
            },
            {
              label: 'X',
              href: 'https://x.com/docusaurus',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/TuOrganizacion/system-control',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} 
System Control, Inc. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
