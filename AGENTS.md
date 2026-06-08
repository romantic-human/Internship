## Goal
Complete all 8 system management modules (backend + frontend) for the Internship project.

## Progress
### Done (M1-M8)
- M1 认证: Backend UserViewSet + frontend login/register/profile/refresh-token/avatar
- M2 菜单: Backend MenuViewSet CRUD + tree/sort/batch-sort + Frontend MenuTree + MenuForm
- M3 权限: Backend PermissionViewSet CRUD + menus binding + Frontend PermissionList + PermissionForm
- M4 部门: Backend DepartmentViewSet CRUD + tree/sort/batch-sort + Frontend DeptTree + DeptForm
- M5 角色: Backend RoleViewSet CRUD + menus assign + users assign + Frontend RoleList + RoleForm
- M6 用户: Backend UserViewSet CRUD + status/reset-password/batch/export/import/avatar/profile + Frontend UserList
- M7 日志: Backend OperationLogViewSet list/clear/export + Frontend LogList (filters/detail/clear/export)
- M8 配置: Backend SystemConfigViewSet CRUD + sort/batch-sort + Frontend ConfigList + ConfigForm
- Seed data: `python manage.py seed` (accounts: `admin/admin123`, `test/test123`)
- Permission granularity: `HasPermission` supports action-level (create→add, update→edit, destroy→delete) + wildcard matching (`user:*`)
- `config:delete` permission seeded
- All backend viewsets have `permission_key` + `get_permissions()` with `IsAuthenticated` + `HasPermission`

### Bug Fixes Applied (complete record)
1. **Menu tree 500 error** (`apps/menu/serializers.py`): `MenuTreeSerializer.get_children` returns serialized data, not raw model objects
2. **Department tree 500 error** (`apps/department/serializers.py`): Same fix as menu tree
3. **Frontend API URL trailing slash mismatches** (4 files): `permission.ts`, `role.ts`, `log.ts`, `config.ts`
4. **Log export ignores filters** (`apps/log/views.py`): `_apply_filters()` shared between `list()` and `export()`
5. **RoleViewSet double-filtering** (`apps/role/views.py`): removed redundant filter in `list()`, moved to `get_queryset()`; fixed `int()` mismatch
6. **user `list()` skips `filter_queryset`** (`apps/user/views.py`): `self.filter_queryset(self.get_queryset())`
7. **Middleware unused `user_id`** (`utils/middleware.py`): removed dead variable
8. **Permission granularity** (`utils/permissions.py`): `HasPermission` now maps create/add, update/edit, destroy/delete
9. **Menu tree() re-fetches Menu.objects.all()** (`apps/menu/views.py`): uses `self.get_queryset()` now
10. **Permission menus() PUT lacks input validation** (`apps/permission/views.py`): `isinstance(menuIds, list)` check
11. **Dead imports** (`apps/user/views.py`): removed `PasswordResetRequest`, `UserUpdateSerializer`, `PasswordResetRequestSerializer`
12. **Seed missing `config:delete`** (`seed.py`): added permission record
13. **Department batch-delete orphan check too strict** (`apps/department/views.py`): `.exclude(id__in=ids)` so parent+children can be deleted together

### Merge Conflicts Resolved (git rebase abca19c)
During `git pull origin develop --rebase`, 6 conflict files were resolved:
1. **MenuTree.vue**: Merged upstream `@selection-change` + `reserve-selection` with stash `stripe` + `<template #empty>`
2. **UserForm.vue**: Kept upstream (no default `password` field) + stash `role_ids: []`
3. **UserList.vue**: Merged upstream with stash batch/export/import buttons + `el-empty` + selection
4. **role/views.py**: Removed duplicate `all` action (upstream already had it); added stash `permission_key` + `get_permissions`
5. **user/serializers.py**: Kept stash fields (`real_name`, `gender`, `department_id`, `role_ids`) for `UserListSerializer` + `UserCreateSerializer`
6. **user/views.py**: Kept stash full CRUD overrides (`get_permissions`, `get_serializer_class`, `create`, `update`, `destroy`, `list`) over upstream minimal version

## Constraints & Conventions
- Backend: `APPEND_SLASH=False` → all API URLs MUST end with `/` (e.g. `/api/permission/` not `/api/permission` or `/api/permission/list`)
- Backend URL prefixes use full names: `api/department/` not `api/dept/`
- `SECRET_KEY` from env or `.env` only
- Frontend: Pinia state, Element Plus UI, TypeScript strict (no `any` where practical)
- All API modules in `Internship-Pre/src/api/`, trailing slash on all endpoints
- Viewsets use `permission_key` class attr + `HasPermission()` + `IsAuthenticated()`; public actions use `AllowAny()`
- Standard CRUD action→permission mapping: create→`entity:add`, update→`entity:edit`, destroy→`entity:delete`
- Custom assign actions (menus, users) use `permission_key_map` override to `entity:assign`
- Responses via `APIResponse.success()` / `APIResponse.error()`

## Project Structure
```
Internship/
├── opencode.json              # opencode project config
├── .opencode/agent/           # custom subagents
├── Internship-core/           # Django backend
│   ├── config/settings.py     # DB: sqlite3, SECRET_KEY/DB_CONN_PASSWORD from .env
│   ├── config/urls.py         # api/<module>/ routes
│   ├── apps/                  # 7 Django apps
│   │   ├── menu/             # MenuViewSet, MenuTreeSerializer
│   │   ├── department/       # DepartmentViewSet, DepartmentTreeSerializer
│   │   ├── permission/       # PermissionViewSet + MenuPermissionRelation
│   │   ├── role/             # RoleViewSet + RoleMenuRelation
│   │   ├── user/             # UserViewSet + UserRoleRelation + seed command
│   │   ├── log/              # OperationLogViewSet (read-only + clear + export)
│   │   └── config_app/       # SystemConfigViewSet
│   └── utils/                # permissions.py, response.py, middleware.py
└── Internship-Pre/           # Vue 3 + TypeScript frontend
    ├── src/api/              # Axios API modules
    ├── src/views/system/     # Page components per module
    ├── src/store/            # Pinia stores
    ├── src/router/           # Routes with meta.layout
    ├── src/layout/           # Layout.vue sidebar (hardcoded nav)
    └── src/utils/            # request.ts (Axios + token refresh)
```

## Accounts
- `admin` / `admin123` — superuser (all permissions)
- `test` / `test123` — normal user (read-only: dept:list, config:list, log:list, user:list, role:list, menu:list, permission:list)

## Running
- Backend: `cd Internship-core && venv\Scripts\python manage.py runserver 0.0.0.0:8000`
- Frontend: `cd Internship-Pre && npm run dev` (serves at http://localhost:3000)
- Seed: `cd Internship-core && venv\Scripts\python manage.py seed`
- Backend Python check: `python manage.py check`
- Frontend type check: `npx vue-tsc --noEmit`
- Frontend build: `npx vite build`

## Git
- Current branch: `feature/lijz`
- Remote: `origin` → git@github.com:romantic-human/Internship.git
- Merge strategy: rebase onto `develop`, then push
- PR: base=`develop` ← head=`feature/lijz`
