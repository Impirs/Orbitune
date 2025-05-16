import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from './stores/user';
import Landing from './pages/Landing.vue';
import Auth from './pages/Auth.vue';
import UserHome from './pages/UserHome.vue';

const routes = [
  { path: '/', component: Landing },
  { path: '/auth', component: Auth },
  { path: '/:user/home', name: 'UserHome', component: UserHome },
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
