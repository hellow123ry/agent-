export type RestaurantRecord = {
  name: string
  type: string
  capacity: number[]
  status: string
}

export type HotelRecord = {
  name: string
  location: string
  type: string
  price: number
  status: string
}

export type KnowledgebasePayload = {
  restaurants: RestaurantRecord[]
  hotels: HotelRecord[]
}

export type KnowledgebaseEnvelope = {
  ok: boolean
  data?: KnowledgebasePayload
  error?: {
    code: string
    message: string
    field?: string | null
  }
}
