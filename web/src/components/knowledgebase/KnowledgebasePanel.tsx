import { useEffect, useMemo, useState } from 'react'
import type { HotelRecord, RestaurantRecord } from '../../types/knowledgebase'

type KnowledgebasePanelProps = {
  restaurants: RestaurantRecord[]
  hotels: HotelRecord[]
  busy: boolean
  error?: string
  onReload: () => Promise<void>
  onSaveRestaurants: (restaurants: RestaurantRecord[]) => Promise<void>
  onSaveHotels: (hotels: HotelRecord[]) => Promise<void>
}

type TabKey = 'restaurants' | 'hotels'

function toCapacityText(capacity: number[]) {
  return capacity.join(', ')
}

function parseCapacityText(value: string) {
  return value
    .split(',')
    .map((item) => Number(item.trim()))
    .filter((item) => Number.isInteger(item) && item > 0)
}

export function KnowledgebasePanel({
  restaurants,
  hotels,
  busy,
  error,
  onReload,
  onSaveRestaurants,
  onSaveHotels,
}: KnowledgebasePanelProps) {
  const [activeTab, setActiveTab] = useState<TabKey>('restaurants')
  const [restaurantDrafts, setRestaurantDrafts] = useState<Array<RestaurantRecord & { capacityText: string }>>([])
  const [hotelDrafts, setHotelDrafts] = useState<HotelRecord[]>([])
  const [saveBusy, setSaveBusy] = useState(false)
  const [localError, setLocalError] = useState<string>()
  const [saveMessage, setSaveMessage] = useState<string>()

  useEffect(() => {
    setRestaurantDrafts(
      restaurants.map((item) => ({
        ...item,
        capacityText: toCapacityText(item.capacity),
      })),
    )
  }, [restaurants])

  useEffect(() => {
    setHotelDrafts(hotels.map((item) => ({ ...item })))
  }, [hotels])

  const activeCount = useMemo(
    () => (activeTab === 'restaurants' ? restaurantDrafts.length : hotelDrafts.length),
    [activeTab, restaurantDrafts.length, hotelDrafts.length],
  )

  function clearFeedback() {
    setLocalError(undefined)
    setSaveMessage(undefined)
  }

  function updateRestaurant(index: number, key: 'name' | 'type' | 'status' | 'capacityText', value: string) {
    clearFeedback()
    setRestaurantDrafts((items) => items.map((item, itemIndex) => (itemIndex === index ? { ...item, [key]: value } : item)))
  }

  function updateHotel(index: number, key: keyof HotelRecord, value: string) {
    clearFeedback()
    setHotelDrafts((items) =>
      items.map((item, itemIndex) =>
        itemIndex === index
          ? {
              ...item,
              [key]: key === 'price' ? Number(value) || 0 : value,
            }
          : item,
      ),
    )
  }

  function addRestaurant() {
    clearFeedback()
    setRestaurantDrafts((items) => [
      ...items,
      { name: '', type: '', capacity: [], capacityText: '2, 4', status: '有位' },
    ])
  }

  function addHotel() {
    clearFeedback()
    setHotelDrafts((items) => [
      ...items,
      { name: '', location: '', type: '', price: 0, status: '有房' },
    ])
  }

  function removeRestaurant(index: number) {
    clearFeedback()
    setRestaurantDrafts((items) => items.filter((_, itemIndex) => itemIndex !== index))
  }

  function removeHotel(index: number) {
    clearFeedback()
    setHotelDrafts((items) => items.filter((_, itemIndex) => itemIndex !== index))
  }

  async function handleSaveRestaurants() {
    clearFeedback()
    const payload = restaurantDrafts.map((item) => ({
      name: item.name.trim(),
      type: item.type.trim(),
      status: item.status.trim(),
      capacity: parseCapacityText(item.capacityText),
    }))
    if (payload.some((item) => item.capacity.length === 0)) {
      setLocalError('餐厅 capacity 请输入正整数，使用逗号分隔。')
      return
    }
    setSaveBusy(true)
    try {
      await onSaveRestaurants(payload)
      setSaveMessage('餐厅知识库已保存')
    } catch (saveError) {
      setLocalError(saveError instanceof Error ? saveError.message : '保存餐厅知识库失败')
    } finally {
      setSaveBusy(false)
    }
  }

  async function handleSaveHotels() {
    clearFeedback()
    const payload = hotelDrafts.map((item) => ({
      ...item,
      name: item.name.trim(),
      location: item.location.trim(),
      type: item.type.trim(),
      status: item.status.trim(),
      price: Number(item.price) || 0,
    }))
    setSaveBusy(true)
    try {
      await onSaveHotels(payload)
      setSaveMessage('酒店知识库已保存')
    } catch (saveError) {
      setLocalError(saveError instanceof Error ? saveError.message : '保存酒店知识库失败')
    } finally {
      setSaveBusy(false)
    }
  }

  return (
    <section className="panel knowledgebase-panel">
      <div className="panel-header">
        <div>
          <h2>知识库编辑</h2>
          <p className="panel-subtitle">直接维护餐厅与酒店样本数据，新会话和新评测会读取最新版本</p>
        </div>
        <button type="button" className="ghost-button" onClick={onReload} disabled={busy || saveBusy}>
          重新加载
        </button>
      </div>
      <div className="knowledgebase-tabs">
        <button
          type="button"
          className={activeTab === 'restaurants' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('restaurants')}
        >
          餐厅
        </button>
        <button
          type="button"
          className={activeTab === 'hotels' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('hotels')}
        >
          酒店
        </button>
        <span className="knowledgebase-count">当前 {activeCount} 条</span>
      </div>
      {error ? <div className="error-banner">{error}</div> : null}
      {localError ? <div className="error-banner">{localError}</div> : null}
      {saveMessage ? <div className="empty-state">{saveMessage}</div> : null}

      {activeTab === 'restaurants' ? (
        <div className="knowledgebase-editor">
          {restaurantDrafts.map((item, index) => (
            <div key={`restaurant-${index}`} className="knowledgebase-card">
              <div className="knowledgebase-card-header">
                <strong>餐厅 {index + 1}</strong>
                <button type="button" className="ghost-button danger-button" onClick={() => removeRestaurant(index)}>
                  删除
                </button>
              </div>
              <div className="knowledgebase-form-grid">
                <label>
                  <span>名称</span>
                  <input value={item.name} onChange={(event) => updateRestaurant(index, 'name', event.target.value)} />
                </label>
                <label>
                  <span>类型</span>
                  <input value={item.type} onChange={(event) => updateRestaurant(index, 'type', event.target.value)} />
                </label>
                <label>
                  <span>容量</span>
                  <input
                    value={item.capacityText}
                    onChange={(event) => updateRestaurant(index, 'capacityText', event.target.value)}
                    placeholder="2, 4, 6"
                  />
                </label>
                <label>
                  <span>状态</span>
                  <input value={item.status} onChange={(event) => updateRestaurant(index, 'status', event.target.value)} />
                </label>
              </div>
            </div>
          ))}
          <div className="knowledgebase-actions">
            <button type="button" className="ghost-button" onClick={addRestaurant} disabled={saveBusy}>
              新增餐厅
            </button>
            <button type="button" onClick={handleSaveRestaurants} disabled={saveBusy}>
              {saveBusy ? '保存中...' : '保存餐厅'}
            </button>
          </div>
        </div>
      ) : (
        <div className="knowledgebase-editor">
          {hotelDrafts.map((item, index) => (
            <div key={`hotel-${index}`} className="knowledgebase-card">
              <div className="knowledgebase-card-header">
                <strong>酒店 {index + 1}</strong>
                <button type="button" className="ghost-button danger-button" onClick={() => removeHotel(index)}>
                  删除
                </button>
              </div>
              <div className="knowledgebase-form-grid">
                <label>
                  <span>名称</span>
                  <input value={item.name} onChange={(event) => updateHotel(index, 'name', event.target.value)} />
                </label>
                <label>
                  <span>位置</span>
                  <input value={item.location} onChange={(event) => updateHotel(index, 'location', event.target.value)} />
                </label>
                <label>
                  <span>类型</span>
                  <input value={item.type} onChange={(event) => updateHotel(index, 'type', event.target.value)} />
                </label>
                <label>
                  <span>价格</span>
                  <input
                    type="number"
                    min={0}
                    value={item.price}
                    onChange={(event) => updateHotel(index, 'price', event.target.value)}
                  />
                </label>
                <label>
                  <span>状态</span>
                  <input value={item.status} onChange={(event) => updateHotel(index, 'status', event.target.value)} />
                </label>
              </div>
            </div>
          ))}
          <div className="knowledgebase-actions">
            <button type="button" className="ghost-button" onClick={addHotel} disabled={saveBusy}>
              新增酒店
            </button>
            <button type="button" onClick={handleSaveHotels} disabled={saveBusy}>
              {saveBusy ? '保存中...' : '保存酒店'}
            </button>
          </div>
        </div>
      )}
    </section>
  )
}
