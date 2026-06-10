"""数据字典模块 — 字典类型 + 字典数据"""
from django.db import models


class DictType(models.Model):
    """字典类型表"""

    dict_name = models.CharField(max_length=100, verbose_name="字典名称")
    dict_type = models.CharField(max_length=100, unique=True, verbose_name="字典类型编码")
    status = models.SmallIntegerField(default=1, verbose_name="状态")
    remark = models.CharField(max_length=500, blank=True, default="", verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "sys_dict_type"
        verbose_name = "字典类型"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]

    def __str__(self):
        return f"{self.dict_name}({self.dict_type})"


class DictData(models.Model):
    """字典数据表"""

    dict_type = models.ForeignKey(
        DictType,
        on_delete=models.CASCADE,
        related_name="data_items",
        to_field="dict_type",
        db_column="dict_type",
        verbose_name="字典类型",
    )
    dict_label = models.CharField(max_length=100, verbose_name="字典标签")
    dict_value = models.CharField(max_length=100, verbose_name="字典键值")
    css_class = models.CharField(max_length=100, blank=True, default="", verbose_name="样式属性")
    list_class = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="表格回显样式（success/warning/danger/info）",
    )
    sort_order = models.IntegerField(default=0, verbose_name="排序号")
    status = models.SmallIntegerField(default=1, verbose_name="状态")
    is_default = models.BooleanField(default=False, verbose_name="是否默认")
    remark = models.CharField(max_length=500, blank=True, default="", verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "sys_dict_data"
        verbose_name = "字典数据"
        verbose_name_plural = verbose_name
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.dict_label}({self.dict_value})"
