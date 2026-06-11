<template>
  <div class="page-container">
    <el-card shadow="never">
      <div class="card-header">
        <el-input v-model="searchName" placeholder="搜索数据源名称" clearable style="width: 240px"
          @clear="fetchData" @keyup.enter="fetchData">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button v-permission="'nl2sql:add'" type="primary" @click="openDialog()">
          <el-icon><Plus /></el-icon> 新增数据源
        </el-button>
      </div>

      <el-table :data="tableData" v-loading="loading" stripe border>
        <template #empty><el-empty description="暂无数据" /></template>
        <el-table-column type="index" label="序号" width="60" align="center"
          :index="(i: number) => (currentPage - 1) * pageSize + i + 1" />
        <el-table-column prop="name" label="数据源名称" min-width="140" />
        <el-table-column prop="db_type" label="类型" width="80" align="center">
          <template #default="{ row }"><el-tag size="small">{{ row.db_type }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="host" label="主机地址" width="150" />
        <el-table-column prop="port" label="端口" width="80" align="center" />
        <el-table-column prop="db_name" label="数据库名" width="140" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建者" width="100" />
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleTest(row)">测试</el-button>
            <el-button v-permission="'nl2sql:edit'" type="primary" link size="small" @click="openDialog(row)">编辑</el-button>
            <el-button v-permission="'nl2sql:delete'" type="danger" link size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 16px; justify-content: flex-end"
        @size-change="currentPage=1;fetchData()"
        @current-change="fetchData"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑数据源' : '新增数据源'" width="520px" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="数据源名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入数据源名称" />
        </el-form-item>
        <el-form-item label="数据库类型" prop="db_type">
          <el-select v-model="form.db_type" style="width: 100%">
            <el-option label="MySQL" value="mysql" />
          </el-select>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="16">
            <el-form-item label="主机地址" prop="host">
              <el-input v-model="form.host" placeholder="127.0.0.1" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="端口" prop="port">
              <el-input-number v-model="form.port" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="数据库名" prop="db_name">
          <el-input v-model="form.db_name" placeholder="请输入数据库名" />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" placeholder="root" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="密码">
              <el-input v-model="form.password_enc" type="password" placeholder="数据库密码" show-password />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox, type FormInstance } from "element-plus";
import { Search, Plus, Connection } from "@element-plus/icons-vue";
import {
  getDataSourceList, createDataSource, updateDataSource, deleteDataSource,
  testDataSourceConnection, type DataSource,
} from "@/api/nl2sql";

const loading = ref(false);
const submitting = ref(false);
const tableData = ref<DataSource[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);
const searchName = ref("");

const dialogVisible = ref(false);
const isEdit = ref(false);
const editId = ref<number | null>(null);
const formRef = ref<FormInstance>();
const form = reactive({
  name: "", db_type: "mysql", host: "127.0.0.1", port: 3306,
  db_name: "", username: "root", password_enc: "",
  description: "", status: 1,
});

const rules = {
  name: [{ required: true, message: "请输入数据源名称", trigger: "blur" }],
  db_name: [{ required: true, message: "请输入数据库名", trigger: "blur" }],
};

function openDialog(row?: DataSource) {
  isEdit.value = !!row;
  if (row) {
    editId.value = row.id;
    form.name = row.name;
    form.db_type = row.db_type;
    form.host = row.host;
    form.port = row.port;
    form.db_name = row.db_name;
    form.username = row.username;
    form.password_enc = "";
    form.description = row.description;
    form.status = row.status;
  } else {
    editId.value = null;
    form.name = "";
    form.db_type = "mysql";
    form.host = "127.0.0.1";
    form.port = 3306;
    form.db_name = "";
    form.username = "root";
    form.password_enc = "";
    form.description = "";
    form.status = 1;
  }
  dialogVisible.value = true;
}

async function fetchData() {
  loading.value = true;
  try {
    const res = await getDataSourceList({
      name: searchName.value || undefined,
      page: currentPage.value,
      pageSize: pageSize.value,
    });
    tableData.value = res.records;
    total.value = res.total;
  } catch { /* handled by interceptor */ }
  finally { loading.value = false; }
}

async function handleSubmit() {
  if (!formRef.value) return;
  try { await formRef.value.validate(); } catch { return; }
  submitting.value = true;
  try {
    const payload = { ...form };
    if (!payload.password_enc) delete (payload as any).password_enc;
    if (isEdit.value && editId.value) {
      await updateDataSource(editId.value, payload);
      ElMessage.success("更新成功");
    } else {
      await createDataSource(payload);
      ElMessage.success("新增成功");
    }
    dialogVisible.value = false;
    fetchData();
  } catch { /* handled by interceptor */ }
  finally { submitting.value = false; }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm("确定删除该数据源？", "提示");
    await deleteDataSource(id);
    ElMessage.success("删除成功");
    fetchData();
  } catch { /* cancel or error */ }
}

async function handleTest(row: DataSource) {
  try {
    await testDataSourceConnection(row.id);
    ElMessage.success("连接成功");
  } catch {
    ElMessage.error("连接失败，请检查配置");
  }
}

onMounted(fetchData);
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
</style>
