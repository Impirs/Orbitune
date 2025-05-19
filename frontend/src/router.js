import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from './stores/user';
import Landing from './pages/out/Landing.vue';
import Auth from './pages/out/Auth.vue';
import UserHome from './pages/UserHome.vue';
import ContentSpotify from './pages/Content_Spotify.vue';
import ContentYouMusic from './pages/Content_YouMusic.vue';
import ContentDiscover from './pages/Content_Discover.vue';

const routes = [
  { path: '/', component: Landing },
  { path: '/auth', component: Auth },
  { path: '/:user/home', name: 'UserHome', component: UserHome },
  { path: '/:user/spotify', name: 'Spotify', component: ContentSpotify },
  { path: '/:user/youtubemusic', name: 'YoutubeMusic', component: ContentYouMusic },
  { path: '/:user/discover', name: 'Discover', component: ContentDiscover },
  {
    path: '/oauth/yandex-music',
    name: 'OauthYandexMusic',
    component: () => import('./pages/out/Oauth_YandexMusic.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const userStore = useUserStore();

  if (!userStore.isLoggedIn) {
    userStore.initialize();
  }

  // Если пользователь залогинен, всегда разрешаем доступ к /:user/home
  if (to.path.match(/^\/[\w-]+\/home/)) {
    if (!userStore.isLoggedIn) {
      userStore.initialize();
      if (!userStore.isLoggedIn) {
        return next('/auth');
      }
    }
    return next();
  }

  if (to.path === '/' && userStore.isLoggedIn) {
    return next(`/${userStore.currentUser.nickname || userStore.currentUser}/home`);
  }

  if (to.path === '/auth') {
    return next();
  }

  if (to.params.user && !userStore.isLoggedIn) {
    return next('/auth');
  }

  next();
});

export default router;
