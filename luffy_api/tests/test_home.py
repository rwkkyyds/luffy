"""
测试首页模块（apps/home/）
============================================================

测试什么：
  1. BannerService 缓存逻辑（缓存命中/未命中时的行为）
  2. BannerView API（轮播图接口）

为什么要 mock cache？
  测试环境没有 Redis，但 BannerService 依赖 Django cache。
  用 @patch('home.service.cache') 替换成假的 cache 对象，
  这样可以精确控制 cache.get 返回什么，验证代码走哪条分支。

mock 的原理：
  原本的 cache.get('banner_list') → 真的去 Redis 查
  mock 之后的 cache.get('banner_list') → 返回你设置的假数据
  这样就能测试"缓存有数据"和"缓存没数据"两种情况
"""
import pytest
from unittest.mock import patch, MagicMock
from django.core.cache import cache

from home.models import Banner
from home.service import BannerService


class TestBannerService:
    @pytest.mark.django_db
    @patch('home.service.cache')  # 把 BannerService 里的 cache 替换成 mock
    def test_get_banner_list_from_db(self, mock_cache):
        """缓存为空时：从数据库查 → 写入缓存 → 返回数据"""
        mock_cache.has_key.return_value = False

        # 在数据库里创建一条 Banner
        Banner.objects.create(title='test', image='banner/test.png', link='http://test.com', info='info', orders=1)

        result = BannerService.get_banner_list()

        # 验证：cache.set 被调用了（数据被写入缓存）
        mock_cache.set.assert_called_once()
        # 验证：返回的是列表
        assert isinstance(result, list)

    @patch('home.service.cache')
    def test_get_banner_list_from_cache(self, mock_cache):
        """缓存命中时：直接返回缓存数据，不查数据库"""
        # 设置 mock：has_key 为 True，get 返回假数据（模拟缓存命中）
        mock_cache.has_key.return_value = True
        cached_data = [{'title': 'cached', 'image': '/img.png', 'link': '/link'}]
        mock_cache.get.return_value = cached_data

        result = BannerService.get_banner_list()

        # 验证：返回的是缓存里的数据
        assert result == cached_data
        # 验证：cache.set 没被调用（没有重新写入缓存）
        mock_cache.set.assert_not_called()

    @patch('home.service.cache')
    def test_invalidate_cache(self, mock_cache):
        """invalidate_cache 应该调用 cache.delete 清除缓存"""
        BannerService.invalidate_cache()
        # 验证：cache.delete 被调用了，key 是 'banner_list'
        mock_cache.delete.assert_called_once_with('banner_list')


class TestBannerAPI:
    @pytest.mark.django_db
    def test_banner_list_empty(self, api_client):
        """没有 Banner 时返回空列表"""
        resp = api_client.get('/api/v1/home/banner/')
        assert resp.data['status'] == 100

    @pytest.mark.django_db
    @patch('home.views.BannerService')  # mock 掉 View 里的 BannerService
    def test_banner_list_with_data(self, mock_service, api_client):
        """有 Banner 时返回数据"""
        # 设置 mock：BannerService.get_banner_list 返回假数据
        mock_service.get_banner_list.return_value = [
            {'title': 'test', 'image': '/img.png', 'link': '/link'}
        ]
        resp = api_client.get('/api/v1/home/banner/')
        assert resp.data['status'] == 100
        assert len(resp.data['result']) == 1
